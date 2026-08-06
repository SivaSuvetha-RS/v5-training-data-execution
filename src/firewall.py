class EvaluationFirewall:
    def __init__(self):
        self.blocked_shards = set()

    def register_eval_shard(self, shard_id):
        self.blocked_shards.add(shard_id)

    def is_allowed(self, shard_id):
        return shard_id not in self.blocked_shards