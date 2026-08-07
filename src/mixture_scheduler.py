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

    def compile_plan(self, index=0):
        stage = self.get_stage(index)
        plan = dict(stage.lane_weights)
        for lane, floor in stage.protected_floors.items():
            plan[lane] = max(plan.get(lane, 0.0), floor)
        total = sum(plan.values())
        if total > 0:
            plan = {lane: value / total for lane, value in plan.items()}
        return plan
