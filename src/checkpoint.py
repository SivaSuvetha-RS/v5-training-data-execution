import json
import os

class CheckpointManager:

    def save(self, step, ledger_offset):
        os.makedirs("submission_artifacts/checkpoints", exist_ok=True)

        checkpoint = {
            "step": step,
            "ledger_offset": ledger_offset
        }

        with open("submission_artifacts/checkpoints/checkpoint.json", "w") as f:
            json.dump(checkpoint, f, indent=4)

        print("[PASS] checkpoint_saved")

    def load(self):
        with open("submission_artifacts/checkpoints/checkpoint.json", "r") as f:
            return json.load(f)