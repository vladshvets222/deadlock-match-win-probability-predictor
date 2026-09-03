import requests
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

URL = 'https://api.deadlock-api.com/v1'

RAW_DATA_DIR = Path("YOUR_DIRECTORY_HERE")
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


class DeadlockAPI:
    def __init__(self):
        self.session = requests.Session()

    def get_recent_matches(self):
        url = f'{URL}/matches/recently-fetched'

        response = self.session.get(url)

        response.raise_for_status()

        return response.json()
    
    def get_match_metadata(self, match_id):
        url = f"{URL}/matches/{match_id}/metadata"

        response = self.session.get(url)

        if response.status_code != 200:
            print(f'Error! Match {match_id}: {response.status_code}')

            return None
        
        return response.json()
    
    def save_match_Data(self, match_id, metadata):
        file_path = RAW_DATA_DIR / f'{match_id}.json'

        with open(file_path, 'w') as f:
            json.dump(metadata, f, indent=2)

    def process_match(self, match):
        match_id = match['match_id']
        file_path = (RAW_DATA_DIR/f'{match_id}.json')

        if file_path.exists():
            return 'already_exists'
        
        metadata = (self.get_match_metadata(match_id))

        if metadata is None:
            return None
        
        self.save_match_Data(match_id,metadata)

        return match_id
    
    def collect_matches(self, max_num_matches=600):
        matches = self.get_recent_matches()
        matches = matches[:max_num_matches]

        print(f'Found {len(matches)} matches')

        successfully_colected = 0

        with ThreadPoolExecutor(max_workers=16) as executor: #!! DEPENDS ON YOUR SYSTEM
            futures = [executor.submit(self.process_match, match) for match in matches]

            for i, future in enumerate(as_completed(futures)):
                result = (future.result())
                if result not in [None, 'already_exists']:
                    successfully_colected += 1
                if i % 50 == 0:
                    print(f'Processed {i} / {len(matches)}')


        print(f"Successfully colected {successfully_colected} matches")



if __name__ == "__main__":
    api = DeadlockAPI()

    api.collect_matches(max_num_matches=600)

