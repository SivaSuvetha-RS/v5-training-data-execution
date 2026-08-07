import uuid

from pipeline.extractor import Extractor
from pipeline.normalizer import TextNormalizer
from pipeline.tokenizer import FrozenTokenizer
from pipeline.shard_builder import ShardBuilder
from pipeline.manifest import Manifest
from pipeline.firewall import EvaluationFirewall


class DataPipeline:
    def __init__(self):
        self.extractor = Extractor()
        self.normalizer = TextNormalizer()
        self.tokenizer = FrozenTokenizer()
        self.shards = ShardBuilder()
        self.manifest = Manifest()
        self.firewall = EvaluationFirewall()
        self.shard_records = []
        self.blocked_documents = []

    def run(self, documents=None):
        if documents is None:
            documents = [{"html": "<html><body><h1>Hello V5</h1></body></html>", "kind": "train"}]

        for index, document in enumerate(documents):
            payload = document if isinstance(document, dict) else {"html": document, "kind": "train"}
            html = payload.get("html", "")
            kind = payload.get("kind", "train")

            text = self.extractor.extract(html)
            text = self.normalizer.normalize(text)

            if not self.firewall.allow(text):
                self.blocked_documents.append({"kind": kind, "reason": "blocked_by_firewall"})
                continue

            tokens = self.tokenizer.tokenize(text)
            shard_id = f"{kind}-{index + 1}-{uuid.uuid4().hex[:8]}"
            shard_path = self.shards.save(shard_id, tokens)

            manifest = self.manifest.create(shard_id, self.tokenizer.tokenizer_hash(), tokens, kind=kind)
            manifest_filename = f"{shard_id}.json"
            self.manifest.save(manifest, manifest_filename)

            self.shard_records.append(
                {
                    "shard_id": shard_id,
                    "kind": kind,
                    "tokens": tokens,
                    "manifest": manifest,
                    "manifest_path": f"submission_artifacts/manifests/{manifest_filename}",
                    "shard_path": shard_path,
                }
            )

        return self.shard_records, self.blocked_documents