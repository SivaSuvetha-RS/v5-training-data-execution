import hashlib
import json
from pathlib import Path


class ReplayManager:
    def __init__(self, root_dir="submission_artifacts"):
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self.history = []
        self.replayed = []

    def build_history_stream(self, batches):
        self.history = []
        for batch in batches:
            token_span = batch.get("token_span", [0, 0])
            payload = {
                "batch_id": batch["batch_id"],
                "token_span": token_span,
                "tokens": batch.get("tokens", []),
                "stage": batch.get("stage"),
                "lane": batch.get("lane"),
            }
            item = {
                "batch_id": batch["batch_id"],
                "token_span": token_span,
                "stage": batch.get("stage"),
                "lane": batch.get("lane"),
                "tokens": batch.get("tokens", []),
                "content_hash": hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest(),
            }
            self.history.append(item)
        return self.history

    def replay_stream(self, stream):
        self.replayed = []
        for item in stream:
            replayed_item = {
                "batch_id": item["batch_id"],
                "token_span": item["token_span"],
                "stage": item.get("stage"),
                "lane": item.get("lane"),
                "tokens": item.get("tokens", []),
                "content_hash": item["content_hash"],
            }
            self.replayed.append(replayed_item)
        return self.replayed

    def audit(self):
        audit_path = self.root_dir / "replay_audit.json"
        payload = {
            "history": self.history,
            "replayed": self.replayed,
        }
        with open(audit_path, "w") as handle:
            json.dump(payload, handle, indent=4)
        return payload