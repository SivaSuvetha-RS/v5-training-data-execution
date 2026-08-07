import hashlib


class EvaluationFirewall:
    def __init__(self):
        self.blocked_shards = set()
        self.blocked_hashes = set()

    def register_eval_shard(self, shard_id):
        self.blocked_shards.add(shard_id)

    def register_eval_data(self, text):
        self.blocked_hashes.add(hashlib.sha256(text.encode()).hexdigest())

    def is_allowed(self, shard_id):
        return shard_id not in self.blocked_shards

    def allow_text(self, text):
        return hashlib.sha256(text.encode()).hexdigest() not in self.blocked_hashes