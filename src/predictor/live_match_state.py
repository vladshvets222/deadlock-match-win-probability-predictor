
class LiveMatchState:

    def __init__(self):

        self.players = {}
        self.game_time = 0
        self.tick = 0
        self.pawn_to_player = {}

    def process_event(self, event_name, data):

        if "game_time" in data:
            self.game_time = max(self.game_time, data['game_time'])

        if "tick" in data:
            self.tick = max(self.tick, data['tick'])

        entity = data.get("entity_type")

        if entity == "player_controller":
            self._update_player_controller(data)
        elif entity == 'player_pawn':
            self._update_player_pawn(data)

    def _update_player_controller(self, data):

        steam_id = data.get('steam_id')

        if steam_id is None or steam_id == 0:
            return None
        
        if steam_id not in self.players:
            self.players[steam_id] = {}

        player = self.players[steam_id]

        pawn = data.get('pawn')
        if pawn is not None:
            self.pawn_to_player[pawn] = steam_id

        mapping = {
            'team': 'team',
            'hero_id': 'hero_id',
            'assigned_lane': 'assigned_lane',
            'kills': 'kills',
            'deaths': 'deaths',
            'assists': 'assists',
            'net_worth': 'net_worth',
            'hero_damage': 'hero_damage',
            'objective_damage': 'objective_damage',
            'hero_healing': 'hero_healing',
            'self_healing': 'self_healing',
            'last_hits': 'last_hits',
            'denies': 'denies'
        }

        for source, target in mapping.items():

            if source in data:
                player[target] = data[source]
                if 'player_slot' in data:
                    player['player_slot'] = data['player_slot']

        player['gold_per_minute'] = (player.get('net_worth', 0) / max(self.game_time / 60, 1))


    def _update_player_pawn(self, data):

        pawn = data.get('entity_index')

        if pawn is None:
            return None
        
        steam_id = (self.pawn_to_player.get(pawn))
        if steam_id is None:
            return None
        
        player = self.players.get(steam_id)
        if player is None:
            return None
        
        if 'level' in data:
            player['level'] = data['level']


    def get_teams(self):

        teams = sorted(set(p['team'] for p in self.players.values() if p.get('team') is not None))

        if len(teams) != 2:
            return None
        
        return ( [p for p in self.players.values() if p['team'] == teams[0]], [p for p in self.players.values() if p['team'] == teams[1]])
    
    def ready(self):

        teams = self.get_teams()

        if teams is None:
            return False
        
        if (len(teams[0]) != 6 or len(teams[1]) != 6):
            return False
        
        for team in teams:
            for p in team:
                if (p.get('level') is None):
                    return False
                
        return True
    
    def summary(self):

        print('-' * 50)

        print(f'Game time: {self.game_time:.0f}s')

        print(f'Players: {len(self.players)}')

        for steam_id, player in self.players.items():
            print(steam_id, player.get('hero_id'), player.get('kills'), player.get('net_worth'), player.get('level'))

        
