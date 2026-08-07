import json
from pathlib import Path

from pipeline.manifest import Manifest
from pipeline.tokenizer import FrozenTokenizer
from pipeline.firewall import EvaluationFirewall
from src.mixture_scheduler import MixtureStage, MixtureScheduler
from src.packing import PackingEngine
from src.masks import create_loss_mask, create_attention_mask, create_position_ids
from src.ledger import ConsumptionLedger, LearningLedger
from src.checkpoint import CheckpointManager
from src.replay import ReplayManager


def test_tokenizer_and_manifest_are_stable():
    tokenizer = FrozenTokenizer()
    text = "hello v5 training data"
    tokens = tokenizer.tokenize(text)
    manifest = Manifest().create("shard-1", tokenizer.tokenizer_hash(), tokens)

    assert tokens == ["hello", "v5", "training", "data"]
    assert manifest["tokenizer_hash"] == tokenizer.tokenizer_hash()
    assert manifest["token_count"] == 4
    assert manifest["content_hash"] == Manifest().create("shard-1", tokenizer.tokenizer_hash(), tokens)["content_hash"]


def test_packing_and_masks_shape_and_padding():
    engine = PackingEngine()
    tokens = list(range(1, 65))
    packed = engine.pack(tokens, sequence_length=32)

    assert len(packed) == 3
    assert packed[0][:32] == list(range(1, 33))
    assert packed[1][:32] == list(range(33, 65))
    assert len(packed[2]) == 32
    assert packed[2][-1] == 0

    loss = create_loss_mask(packed[0])
    attention = create_attention_mask(packed[0])
    positions = create_position_ids(packed[0])

    assert len(loss) == 32
    assert sum(loss) == 32
    assert attention.count(1) == 32
    assert positions[0] == 0 and positions[-1] == 31


def test_mixture_schedule_honors_protected_floors():
    scheduler = MixtureScheduler()
    scheduler.add_stage(
        MixtureStage(
            name="pretraining",
            lane_weights={"general": 0.5, "code": 0.2, "indic": 0.1, "reasoning": 0.2},
            protected_floors={"indic": 0.08, "reasoning": 0.05},
        )
    )

    plan = scheduler.compile_plan(0)

    assert plan["general"] >= 0.5
    assert plan["indic"] >= 0.08
    assert plan["reasoning"] >= 0.05
    assert sum(plan.values()) == 1.0


def test_firewall_blocks_eval_data():
    firewall = EvaluationFirewall()
    firewall.register_eval_data("eval document")

    assert firewall.allow("train document") is True
    assert firewall.allow("eval document") is False


def test_checkpoint_resume_and_replay_are_consistent(tmp_path):
    ledger = ConsumptionLedger()
    ledger.record({"step": 1, "batch_id": "batch-001", "tokens": 32})
    ledger.record({"step": 2, "batch_id": "batch-002", "tokens": 32})

    checkpoint = CheckpointManager(root_dir=str(tmp_path))
    checkpoint.save(step=2, ledger_offset=1, batch_id="batch-002")
    loaded = checkpoint.load()

    assert loaded["step"] == 2
    assert loaded["ledger_offset"] == 1
    assert loaded["batch_id"] == "batch-002"

    replay = ReplayManager(root_dir=str(tmp_path))
    stream = replay.build_history_stream([{"batch_id": "batch-001"}, {"batch_id": "batch-002"}])
    replayed = replay.replay_stream(stream)

    assert replayed[0]["batch_id"] == "batch-001"
    assert replayed[1]["batch_id"] == "batch-002"
