import json

class ConsumptionLedger:
    def __init__(self):
        self.events = []

    def record(self, event):
        self.events.append(event)

    def save(self, path):
        with open(path, "w") as f:
            json.dump(self.events, f, indent=4)


class LearningLedger:
    def __init__(self):
        self.records = []

    def record(self, data):
        self.records.append(data)

    def save(self, path):
        with open(path, "w") as f:
            json.dump(self.records, f, indent=4)
