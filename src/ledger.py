import json
from pathlib import Path


class ConsumptionLedger:
    def __init__(self):
        self.events = []

    def record(self, event):
        self.events.append(event)

    def save(self, path):
        out_path = Path(path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as handle:
            json.dump(self.events, handle, indent=4)


class LearningLedger:
    def __init__(self):
        self.records = []

    def record(self, data):
        self.records.append(data)

    def save(self, path):
        out_path = Path(path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as handle:
            json.dump(self.records, handle, indent=4)
