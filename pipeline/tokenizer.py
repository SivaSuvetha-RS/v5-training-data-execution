import hashlib


class FrozenTokenizer:
    VERSION = "v1"
    PAD_TOKEN = "<pad>"
    UNK_TOKEN = "<unk>"

    def _token_id(self, token: str) -> int:
        if token == self.PAD_TOKEN:
            return 0
        if token == self.UNK_TOKEN:
            return 1
        digest = hashlib.sha256(token.encode()).hexdigest()
        return 2 + int(digest[:8], 16) % 1000000

    def tokenize(self, text):
        return [self._token_id(token) for token in text.split()]

    def tokenizer_hash(self):
        return hashlib.sha256(self.VERSION.encode()).hexdigest()
