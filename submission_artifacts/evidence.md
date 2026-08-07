# Evidence Report

- tokenizer_integrity: PASS
  - Tokenizer hash and manifest content hash matched the recorded shard manifest.
- evaluation_firewall: PASS
  - Training shards were allowed while evaluation shards were blocked.
- packing_correctness: PASS
  - Packed batches preserved sequence length and mask semantics.
- mixture_compliance: PASS
  - The mixture plan respected the stage weights and protected floors.
- opus_audit_trail: PASS
  - OPUS acceptance, rejection, deferral, and override decisions were recorded.
- crash_recovery: PASS
  - The saved checkpoint resumed the exact next batch without skipping or repeating.
- replay: PASS
  - Original and replayed batch ids, token spans, and hashes matched.
- learning_trace: PASS
  - Learning records were linked to the consumed batches and loss traces.
- throughput: PASS
  - Packing efficiency and useful loss-bearing tokens per second were measured.
