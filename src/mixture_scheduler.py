from dataclasses import dataclass

@dataclass
class MixtureStage:
    name: str
    lane_weights: dict
    protected_floors: dict


class MixtureScheduler:
    def __init__(self):
        self.stages = []

    def add_stage(self, stage: MixtureStage):
        self.stages.append(stage)

    def get_stage(self, index):
        return self.stages[index]
