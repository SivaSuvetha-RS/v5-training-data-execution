import hashlib


class EvaluationFirewall:

    def __init__(self):

        self.blocked_hashes = set()

    def register_eval_data(self, text):

        h = hashlib.sha256(text.encode()).hexdigest()

        self.blocked_hashes.add(h)

    def allow(self, text):

        h = hashlib.sha256(text.encode()).hexdigest()

        return h not in self.blocked_hashes