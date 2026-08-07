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

    def run(self):

        sample_html = """
        <html>
        <body>
        <h1>Hello V5</h1>
        <p>This is a training document.</p>
        </body>
        </html>
        """

        text = self.extractor.extract(sample_html)

        text = self.normalizer.normalize(text)

        if not self.firewall.allow(text):
            print("Evaluation data blocked.")
            return

        tokens = self.tokenizer.tokenize(text)

        shard_id = str(uuid.uuid4())

        self.shards.save(shard_id, tokens)

        manifest = self.manifest.create(
            shard_id,
            self.tokenizer.tokenizer_hash(),
            tokens
        )

        self.manifest.save(
            manifest,
            f"{shard_id}.json"
        )