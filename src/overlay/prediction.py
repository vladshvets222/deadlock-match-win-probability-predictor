import json
import os


class PredictionManager:

    def __init__(self, filename):
        self.filename = filename

    def get_prediction(self):
        if not os.path.exists(self.filename):
            return None
        try:
            with open(self.filename, "r") as f:
                return json.load(f)
        except Exception:
            return None