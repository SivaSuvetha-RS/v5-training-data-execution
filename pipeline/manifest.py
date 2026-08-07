import hashlib
import json
from pathlib import Path


class Manifest:
    def create(self, shard_id, tokenizer_hash, tokens, kind="train"):
        content = " ".join(str(token) for token in tokens)
        return {
            "shard_id": shard_id,
            "kind": kind,
            "tokenizer_hash": tokenizer_hash,
            "token_count": len(tokens),
            "content_hash": hashlib.sha256(content.encode()).hexdigest(),
        }

    def save(self, manifest, filename):
        out_dir = Path("submission_artifacts/manifests")
        out_dir.mkdir(parents=True, exist_ok=True)
        with open(out_dir / filename, "w") as handle:
            json.dump(manifest, handle, indent=4)

    def validate(self, manifest, tokenizer_hash, tokens):
        expected = self.create(manifest["shard_id"], tokenizer_hash, tokens, manifest.get("kind", "train"))
        return (
            manifest["tokenizer_hash"] == expected["tokenizer_hash"]
            and manifest["token_count"] == expected["token_count"]
            and manifest["content_hash"] == expected["content_hash"]
        )