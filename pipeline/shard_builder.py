import json
from pathlib import Path


class ShardBuilder:
    def save(self, shard_id, tokens, root_dir="data/shards"):
        out_dir = Path(root_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        filename = out_dir / f"{shard_id}.json"
        with open(filename, "w") as handle:
            json.dump(tokens, handle, indent=2)
        return str(filename)