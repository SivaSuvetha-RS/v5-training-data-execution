import json
from pathlib import Path


class CheckpointManager:
    def __init__(self, root_dir="submission_artifacts/checkpoints"):
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def save(self, step, ledger_offset, batch_id=None, history_hash=None):
        checkpoint = {
            "step": step,
            "ledger_offset": ledger_offset,
            "batch_id": batch_id,
            "history_hash": history_hash,
        }
        with open(self.root_dir / "checkpoint.json", "w") as handle:
            json.dump(checkpoint, handle, indent=4)
        return checkpoint

    def load(self):
        with open(self.root_dir / "checkpoint.json", "r") as handle:
            return json.load(handle)