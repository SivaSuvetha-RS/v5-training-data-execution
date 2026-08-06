import hashlib
import json
from pathlib import Path


class Manifest:

    def create(self,
               shard_id,
               tokenizer_hash,
               tokens):

        return {

            "shard_id": shard_id,

            "tokenizer_hash": tokenizer_hash,

            "token_count": len(tokens),

            "content_hash":
            hashlib.sha256(
                " ".join(tokens).encode()
            ).hexdigest()

        }

    def save(self,
             manifest,
             filename):

        Path("submission_artifacts/manifests").mkdir(
            parents=True,
            exist_ok=True)

        with open(
            f"submission_artifacts/manifests/{filename}",
            "w"
        ) as f:

            json.dump(
                manifest,
                f,
                indent=4)