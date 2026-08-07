# V5 Training Data Execution System

This repository implements a compact but complete training-data execution pipeline for V5. The system is designed to show how documents flow through tokenization, manifest creation, mixture planning, packing, batching, ledger tracking, checkpointing, crash recovery, replay, and audit in a reproducible way.

## Architecture

The pipeline follows this execution path:

1. Documents are extracted and normalized.
2. A frozen tokenizer produces immutable tokenized shards.
3. Each shard is paired with a manifest containing tokenizer and content hashes.
4. A mixture scheduler compiles lane weights and protected floors.
5. A packing engine builds deterministic batches with loss, attention, and position masks.
6. Consumption and learning ledgers record what was used and what the model learned.
7. Checkpoints store ledger offsets and batch state for crash recovery.
8. Replay and audit utilities reconstruct a historical stream and verify batch hashes.
9. Evidence and performance generators write the required machine-readable reports.

This keeps the system auditable because each step produces artifacts that can be inspected later.

## Repository directory guide

- [run_demo.py](run_demo.py) — entry point that runs the full demonstration.
- [pipeline/](pipeline/) — core data pipeline implementation.
  - [pipeline/pipeline.py](pipeline/pipeline.py) — orchestrates document → shard → manifest processing.
  - [pipeline/tokenizer.py](pipeline/tokenizer.py) — frozen tokenizer implementation.
  - [pipeline/manifest.py](pipeline/manifest.py) — manifest creation and validation logic.
  - [pipeline/shard_builder.py](pipeline/shard_builder.py) — writes shard payloads to disk.
  - [pipeline/firewall.py](pipeline/firewall.py) — evaluation-data blocking logic.
- [src/](src/) — training execution helpers and bookkeeping modules.
  - [src/mixture_scheduler.py](src/mixture_scheduler.py) — mixture stages, lane weights, and protected floors.
  - [src/packing.py](src/packing.py) — batch packing and padding logic.
  - [src/masks.py](src/masks.py) — loss, attention, and position mask helpers.
  - [src/ledger.py](src/ledger.py) — consumption and learning ledger storage.
  - [src/checkpoint.py](src/checkpoint.py) — crash-safe checkpointing.
  - [src/replay.py](src/replay.py) — replay and audit support.
  - [src/evidence.py](src/evidence.py) — evidence bundle generation.
  - [src/performance.py](src/performance.py) — packing and throughput reporting.
- [tests/](tests/) — regression tests for the main invariants.
- [submission_artifacts/](submission_artifacts/) — generated outputs such as logs, manifests, ledgers, checkpoints, replay audit, and evidence reports.
- [data/](data/) and [config/](config/) — sample input and runtime data locations.

## Design decisions

- The tokenizer is intentionally frozen and versioned so shard manifests remain reproducible.
- Shard manifests are content-addressed and validated against the token stream.
- Evaluation data is blocked by the firewall to preserve training integrity.
- Checkpoints are tied to the next expected batch so resume does not skip or repeat work.
- Replay uses deterministic hashes so historical reconstruction can be verified.

## Run

Use:

```bash
python run_demo.py
```

This produces the complete demonstration, including logs, manifests, ledgers, checkpoints, replay evidence, and performance reports in the submission_artifacts directory.
