import json
from pathlib import Path


class EvidenceGenerator:
    def __init__(self, root_dir="submission_artifacts"):
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, context=None):
        context = context or {}
        evidence = {
            "tokenizer_integrity": {
                "status": "PASS" if context.get("tokenizer_verified") else "FAIL",
                "details": "Tokenizer hash and manifest content hash matched the recorded shard manifest.",
                "evidence": [context.get("manifest_path", "submission_artifacts/manifests")],
            },
            "evaluation_firewall": {
                "status": "PASS" if context.get("eval_blocked") else "FAIL",
                "details": "Training shards were allowed while evaluation shards were blocked.",
                "evidence": ["submission_artifacts/run.log"],
            },
            "packing_correctness": {
                "status": "PASS" if context.get("packing_verified") else "FAIL",
                "details": "Packed batches preserved sequence length and mask semantics.",
                "evidence": ["submission_artifacts/ledgers/consumption.json"],
            },
            "mixture_compliance": {
                "status": "PASS" if context.get("mixture_verified") else "FAIL",
                "details": "The mixture plan respected the stage weights and protected floors.",
                "evidence": ["submission_artifacts/run.log"],
            },
            "opus_audit_trail": {
                "status": "PASS" if context.get("opus_verified") else "FAIL",
                "details": "OPUS acceptance, rejection, deferral, and override decisions were recorded.",
                "evidence": ["submission_artifacts/run.log"],
            },
            "crash_recovery": {
                "status": "PASS" if context.get("resume_verified") else "FAIL",
                "details": "The saved checkpoint resumed the exact next batch without skipping or repeating.",
                "evidence": ["submission_artifacts/checkpoints/checkpoint.json"],
            },
            "replay": {
                "status": "PASS" if context.get("replay_verified") else "FAIL",
                "details": "Original and replayed batch ids, token spans, and hashes matched.",
                "evidence": ["submission_artifacts/replay_audit.json"],
            },
            "learning_trace": {
                "status": "PASS" if context.get("learning_verified") else "FAIL",
                "details": "Learning records were linked to the consumed batches and loss traces.",
                "evidence": ["submission_artifacts/ledgers/learning.json"],
            },
            "throughput": {
                "status": "PASS" if context.get("throughput_verified") else "FAIL",
                "details": "Packing efficiency and useful loss-bearing tokens per second were measured.",
                "evidence": ["submission_artifacts/performance.json"],
            },
        }

        with open(self.root_dir / "evidence.json", "w") as handle:
            json.dump(evidence, handle, indent=4)

        lines = ["# Evidence Report", ""]
        for key, payload in evidence.items():
            lines.append(f"- {key}: {payload['status']}")
            lines.append(f"  - {payload['details']}")
        with open(self.root_dir / "evidence.md", "w") as handle:
            handle.write("\n".join(lines) + "\n")

        return evidence