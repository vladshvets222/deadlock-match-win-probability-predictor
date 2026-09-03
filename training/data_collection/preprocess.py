import json
from pathlib import Path
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import as_completed

RAW_DATA_DIR = Path('YOUR_PATH_HERE')

def laod_match(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)
    
def get_10min_snapshot(player):

    stats = player.get('stats', [])

    if len(stats) == 0:
        return None
    
    valid_stats = [
        s for s in stats
        if 540 <= s["time_stamp_s"] <= 660
    ]

    if len(valid_stats) == 0:
        return None
    
    target_time = 600

    closest_to10min_stats = min(valid_stats,key=lambda x: abs(x["time_stamp_s"] - target_time))

    return closest_to10min_stats

def build_team_row(match_id, winning_team, team_id, players):

    row = {
        'match_id': match_id,
        'team': team_id,

        'won' : int(team_id == winning_team)}

    processed_players = []

    for player in players:
        snapshot = get_10min_snapshot(player)
        if snapshot is None:
            continue

        processed_players.append({
            'hero_id': player.get('hero_id'),
            "assigned_lane":player.get("assigned_lane",-1),
            "kills":snapshot.get("kills",0),
            "deaths":snapshot.get("deaths",0),
            "assists":snapshot.get("assists",0),
            "net_worth":snapshot.get("net_worth",0),
            "player_damage":snapshot.get("player_damage", 0),
            "creep_kills":snapshot.get("creep_kills",0),
            "level": snapshot.get("level",0),
            'objective_damage': snapshot.get('boss_damage', 0),
            'denies': snapshot.get('denies', 0),
            'player_healing': snapshot.get('player_healing', 0),
            'self_healing': snapshot.get('self_healing', 0),
            'gold_per_minute': snapshot.get('net_worth', 0) / (snapshot.get('time_stamp_s', 600) / 60 + 1e-6)
        })
    
    if len(processed_players) != 6:
        return None
    
    processed_players.sort(key=lambda x: x['net_worth'], reverse=True)

    row['team_total_kills'] = sum(p['kills'] for p in processed_players)
    row['team_total_deaths'] = sum(p['deaths'] for p in processed_players)
    row['team_total_networth'] = sum(p['net_worth'] for p in processed_players)
    row['team_total_damage'] = sum(p['player_damage'] for p in processed_players)
    row['team_total_objectivedamage'] = sum(p['objective_damage'] for p in processed_players)
    row['team_avg_level'] = sum(p['level'] for p in processed_players)/6
    row['team_gold_per_minute'] = sum(p['gold_per_minute'] for p in processed_players)/6

    for i,p in enumerate(processed_players):

        prefix=f"p{i+1}"

        row[f"{prefix}_hero"] = p["hero_id"]
        row[f"{prefix}_lane"] = p["assigned_lane"]
        row[f"{prefix}_kills"] = p["kills"]
        row[f"{prefix}_deaths"] = p["deaths"]
        row[f"{prefix}_assists"] = p["assists"]
        row[f"{prefix}_networth"] = p["net_worth"]
        row[f"{prefix}_damage"] = p["player_damage"]
        row[f"{prefix}_creeps"] = p["creep_kills"]
        row[f"{prefix}_level"] = p["level"]
        row[f"{prefix}_objective_damage"] = p["objective_damage"]
        row[f"{prefix}_denies"] = p["denies"]
        row[f"{prefix}_gold_per_minute"] = p["gold_per_minute"]
        row[f"{prefix}_player_healing"] = p["player_healing"]
        row[f"{prefix}_self_healing"] = p["self_healing"]


    return row


def parse_match(metadata):
    match_info = metadata['match_info']

    winning_team = match_info['winning_team']

    players = match_info['players']

    match_id = metadata['match_id']

    team0 = [p for p in players if p['team'] == 0]
    team1 = [p for p in players if p['team'] == 1]

    row0 = build_team_row(match_id, winning_team, 0, team0)
    row1 = build_team_row(match_id, winning_team, 1, team1)
    if row0 is None or row1 is None:
        return None

    combined = {"match_id": match_id,"team0_won":int(winning_team==0)}
    for k,v in row0.items():
        if k in ["match_id","team","won"]:
            continue
        combined[f"team0_{k}"] = v

    for k,v in row1.items():
        if k in ["match_id","team","won"]:
            continue
        combined[ f"team1_{k}"] = v

    return combined

def process_file(file_path):
    try:
        metadata = laod_match(file_path)
        metadata['match_id'] = int(file_path.stem)
        row = parse_match(metadata)
        return row
    except Exception as e:
        print(f'Error processing {file_path.name}: {e}')
        return None

def create_dataset():
    all_rows = []

    files = list(RAW_DATA_DIR.glob('*.json'))

    print(f'Found {len(files)} files to create dataset')

    with ProcessPoolExecutor(max_workers=12) as executor: #!! DEPENDS ON YOUR SYSTEM
        futures = [executor.submit(process_file, file_path) for file_path in files]
        for i, future in enumerate(as_completed(futures)):
            row = future.result()
            if row is not None:
                all_rows.append(row)
            if i % 100 == 0:
                print(f'Processed {i} / {len(files)}')

    df = pd.DataFrame(all_rows)

    return df


if __name__ == '__main__':
    df = create_dataset()
    print(df.shape)
    print(df.head)
    df.to_csv(r"YOUR_PATH_HERE", index = False)

    