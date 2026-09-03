import json
import time
import requests
import pandas as pd
import joblib
import argparse
import os

from sseclient import SSEClient

from live_match_state import LiveMatchState
from feature_builder import build_match_features
from ensemble_model import EnsembleModel

LIVE_SERVER = "http://localhost:3000"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

APP_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

MODELS_DIR = os.path.join(APP_DIR, "models")

SHARED_DIR = os.path.join(APP_DIR, "shared")

PREDICTION_FILE = os.path.join(SHARED_DIR, "prediction.json")

MODELS = {
    5: joblib.load(os.path.join(MODELS_DIR, "ensemble_5min.pkl")),
    10: joblib.load(os.path.join(MODELS_DIR, "ensemble_10min.pkl")),
    15: joblib.load(os.path.join(MODELS_DIR, "ensemble_15min.pkl")),
    20: joblib.load(os.path.join(MODELS_DIR, "ensemble_20min.pkl")),
    25: joblib.load(os.path.join(MODELS_DIR, "ensemble_25min.pkl")),
    30: joblib.load(os.path.join(MODELS_DIR, "ensemble_30min.pkl")),
    35: joblib.load(os.path.join(MODELS_DIR, "ensemble_35min.pkl")),
    40: joblib.load(os.path.join(MODELS_DIR, "ensemble_40min.pkl")),
}

FEATURES_PATH = os.path.join(MODELS_DIR, "feature_columns.pkl")


def get_live_match():
    response = requests.get("https://api.deadlock-api.com/v1/matches/live/urls")
    response.raise_for_status()
    matches = response.json()
    return matches[0]['match_id']

def build_prediction_df(row, feature_columns):

    df = pd.DataFrame([row])
    df = df.reindex(columns=feature_columns, fill_value=0)
    return df[feature_columns]

def connect_stream(match_id):
    url = (f'{LIVE_SERVER}/v1/matches/{match_id}/live/demo/events')         # ?subscribed_entities=player_controller,player_pawn
    print('-' * 50)
    print(f'Connecting: {url}')
    response = requests.get(url, stream=True)
    response.raise_for_status()
    return SSEClient(response)

def get_model_for_time(game_time_seconds):
    minutes = game_time_seconds / 60
    if minutes < 7.5:
        return MODELS[5], '5min'
    elif minutes < 12.5:
        return MODELS[10], '10min'
    elif minutes < 17.5:
        return MODELS[15], '15min'
    elif minutes < 22.5:
        return MODELS[20], '20min'
    elif minutes < 27.5:
        return MODELS[25], '25min'
    elif minutes < 32.5:
        return MODELS[30], '30min'
    elif minutes < 37.5:
        return MODELS[35], '35min'
    else:
        return MODELS[40], '40min'

def parse_args():

    parser = argparse.ArgumentParser(
        description="Deadlock Live Match Predictor"
    )

    parser.add_argument(
        "--match",
        type=int,
        help="Specific match ID to predict"
    )

    return parser.parse_args()

def wait_for_server(timeout=30):

    print("Waiting for live-events server...")

    start = time.time()

    while True:
        try:
            response = requests.get("http://localhost:3000")

            if response.status_code < 500:
                print("Server is ready.")
                return

        except requests.exceptions.ConnectionError:
            pass

        if time.time() - start > timeout:
            raise RuntimeError("Timed out waiting for live-events server.")
        time.sleep(0.5)

def main():

    print('-' * 50)
    feature_columns = joblib.load(FEATURES_PATH)
    args = parse_args()
    if args.match is not None:
        match_id = args.match
        print(f"Using specified match: {match_id}")
    else:
        match_id = get_live_match()
        print(f"Using latest live match: {match_id}")
    wait_for_server()
    client = connect_stream(match_id)
    state = LiveMatchState()
    last_prediction_minute = -1
    for event in client.events():
        try:
            data = json.loads(event.data)
        except:
            continue

        state.process_event(event.event, data)
        if not state.ready():
            continue
        
        current_minute = int(state.game_time // 60)
        if current_minute == last_prediction_minute:
            continue
        last_prediction_minute = current_minute
        try:
            row = build_match_features(state)
            if row is None:
                continue
            X = build_prediction_df(row, feature_columns)
            game_time = state.game_time
            model, model_name = get_model_for_time(game_time)
            prob = (model.predict_proba(X)[0][1])
            print('-'* 50)
            minutes = int(state.game_time // 60)
            seconds = int(state.game_time % 60)

            prediction = {
                'minute': minutes,
                'seconds': seconds,
                'probability': float(prob),
                'model': model_name
            }
            with open(PREDICTION_FILE, 'w') as f:
                json.dump(prediction, f)

            print(f'Game Time: {minutes:02d}m {seconds:02d}s')
            print(f"Using model: {model_name}")
            print(f'Team0 Win: {prob:.2%}')
            print(f'Team1 Win: {(1-prob):.2%}')
        except Exception as e:
            print('Prediction error')
            print(e)

if __name__ == '__main__':
    main()

