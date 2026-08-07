import hashlib


class FrozenTokenizer:
    VERSION = "v1"

    def tokenize(self, text):
        return text.split()

    def tokenizer_hash(self):
        return hashlib.sha256(self.VERSION.encode()).hexdigest()