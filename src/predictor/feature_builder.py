import numpy as np
import pandas as pd

def build_team_features(players, team_name, game_time):

    row = {}

    players = sorted(players, key=lambda x: x['net_worth'], reverse=True)

    row[f'{team_name}_team_total_kills'] = sum(p['kills'] for p in players)
    row[f'{team_name}_team_total_deaths'] = sum(p['deaths'] for p in players)
    row[f'{team_name}_team_total_networth'] = sum(p['net_worth'] for p in players)
    row[f'{team_name}_team_total_damage'] = sum(p['hero_damage'] for p in players)
    row[f'{team_name}_team_total_objectivedamage'] = sum(p['objective_damage'] for p in players)
    row[f'{team_name}_team_avg_level'] = (sum(p['level'] for p in players) / 6)
    row[f'{team_name}_team_gold_per_minute'] = (sum(p['gold_per_minute'] for p in players) / 6)

    for i, p in enumerate(players, start=1):

        prefix = f'{team_name}_p{i}'

        row[f'{prefix}_kills'] = p['kills']
        row[f'{prefix}_deaths'] = p['deaths']
        row[f'{prefix}_assists'] = p['assists']
        row[f'{prefix}_networth'] = p['net_worth']
        row[f'{prefix}_damage'] = p['hero_damage']
        row[f'{prefix}_creeps'] = p['last_hits']
        row[f'{prefix}_level'] = p['level']
        row[f'{prefix}_objective_damage'] = p['objective_damage']
        row[f'{prefix}_denies'] = p['denies']
        row[f'{prefix}_gold_per_minute'] = (p['net_worth'] / max(game_time / 60, 1))
        row[f'{prefix}_player_healing'] = (p['hero_healing'])
        row[f'{prefix}_self_healing'] = (p['self_healing'])
        row[f'{prefix}_hero'] = (p['hero_id'])
        row[f'{prefix}_lane'] = (p['assigned_lane'])

    return row
    
def build_match_features(state):

    teams = sorted(set(p['team'] for p in state.players.values() if p.get('team') is not None))

    if len(teams) != 2:
        return None

    team0_id = teams[0]
    team1_id = teams[1]

    team0 = [p for p in state.players.values() if p['team'] == team0_id]
    team1 = [p for p in state.players.values() if p['team'] == team1_id]

    if len(team0) != 6:
        return None
    if len(team1) != 6:
        return None
    
    row = {}

    row.update(build_team_features(team0, 'team0', state.game_time))
    row.update(build_team_features(team1, 'team1', state.game_time))

    #Engineered features

    row['team0_carry_share'] = (row['team0_p1_networth'] / row['team0_team_total_networth'])
    row['team1_carry_share'] = (row['team1_p1_networth'] / row['team1_team_total_networth'])

    row['team0_networth_std'] = np.std([row[f'team0_p{i}_networth'] for i in range(1, 7)])
    row['team1_networth_std'] = np.std([row[f'team1_p{i}_networth'] for i in range(1, 7)])

    row['team0_team_kdr'] = (row['team0_team_total_kills'] / (row['team0_team_total_deaths'] + 1))
    row['team1_team_kdr'] = (row['team1_team_total_kills'] / (row['team1_team_total_deaths'] + 1))

    row['team0_richest_vs_team_avg'] = (row['team0_p1_networth'] / (row['team0_team_total_networth'] / 6))
    row['team1_richest_vs_team_avg'] = (row['team1_p1_networth'] / (row['team1_team_total_networth'] / 6))


    row['networth_diff'] = (row['team0_team_total_networth'] - row['team1_team_total_networth'])
    row['damage_diff'] = (row['team0_team_total_damage'] - row['team1_team_total_damage'])
    row['level_diff'] = (row['team0_team_avg_level'] - row['team1_team_avg_level'])
    row['carry_diff'] = (row['team0_p1_networth'] - row['team1_p1_networth'])
    row['kdr_diff'] = (row['team0_team_kdr'] - row['team1_team_kdr'])
    row['gpm_diff'] = (row['team0_team_gold_per_minute'] - row['team1_team_gold_per_minute'])
    row['objective_diff'] = (row['team0_team_total_objectivedamage'] - row['team1_team_total_objectivedamage'])

    row['networth_ratio'] = (row['team0_team_total_networth'] / (row['team1_team_total_networth'] + 1))
    row['damage_ratio'] = (row['team0_team_total_damage'] / (row['team1_team_total_damage'] + 1))
    row['objective_ratio'] = (row['team0_team_total_objectivedamage'] / (row['team1_team_total_objectivedamage'] + 1))

    HERO_IDS = [
    1,2,3,4,6,7,8,10,11,12,13,14,15,16,17,18,19,
    20,25,27,
    31,35,
    50,52,58,
    60,63,64,65,66,67,69,
    72,76,77,79,80,81
    ]

    LANES = [1,3,4,6]


    for team in [0,1]:
        for i in range(1,7):
            hero_col = (f'team{team}_p{i}_hero')
            lane_col = (f'team{team}_p{i}_lane')
            hero = row.get(hero_col, -1)
            lane = row.get(lane_col, -1)

            for h in HERO_IDS:
                row[f'{hero_col}_{h}'] = int(hero == h)
            for l in LANES:
                row[f'{lane_col}_{l}'] = int(lane == l)

            del row[hero_col]
            del row[lane_col]

    return row