import json
from pathlib import Path


class ShardBuilder:

    def save(self, shard_id, tokens):

        Path("data/shards").mkdir(
            parents=True,
            exist_ok=True
        )

        filename = f"data/shards/{shard_id}.json"

        with open(filename, "w") as f:
            json.dump(tokens, f, indent=2)

        return filename