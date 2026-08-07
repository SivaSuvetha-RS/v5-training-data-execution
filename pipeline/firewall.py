import hashlib


class EvaluationFirewall:
    def __init__(self):
        self.blocked_hashes = set()
        self.blocked_shards = set()

    def register_eval_data(self, text):
        h = hashlib.sha256(text.encode()).hexdigest()
        self.blocked_hashes.add(h)
        return h

    def register_eval_shard(self, shard_id):
        self.blocked_shards.add(shard_id)

    def allow(self, text):
        h = hashlib.sha256(text.encode()).hexdigest()
        return h not in self.blocked_hashes

    def is_allowed(self, shard_id):
        return shard_id not in self.blocked_shards