# Session 5: Mixture & Curriculum Plan

## Overview

Building a capable foundation model requires more than collecting a large amount of text. The quality, diversity, ordering, and distribution of the training corpus directly influence the model's final capabilities. A poorly balanced dataset can produce a model that is strong in one domain but weak in reasoning, multilingual understanding, or programming.

The objective of this proposal is to design a balanced pre-training strategy for V5 that develops multiple capabilities simultaneously while ensuring that no important skill is neglected. Instead of relying on a single massive corpus, the training data is divided into capability-oriented collections and introduced progressively through curriculum learning.

Every major decision in this plan is treated as a hypothesis and should be validated through small-scale proxy experiments before large-scale training is trusted.

## Design Goals

The proposed strategy focuses on five major goals:

- Strong general intelligence through broad language understanding, factual recall, summarization, and conversational ability.
- Reliable programming skills for code generation, explanation, debugging, and software reasoning.
- Advanced reasoning for mathematical thinking, logical deduction, and multi-step problem solving.
- Multilingual capability with strong support for Indic languages without sacrificing English performance.
- Efficient resource utilization by ensuring each training token contributes meaningful learning rather than redundant or low-quality signal.

## Training Philosophy

V5 follows a staged learning approach. The model first learns general language structure, then gradually absorbs more challenging data such as programming, scientific documents, and reasoning examples. This progression reduces optimization instability and improves intermediate representations before difficult tasks are introduced.

The training philosophy is guided by four principles:

- High-quality data is more valuable than raw scale.
- Different capabilities require different proportions of training data.
- Rare but important capabilities must remain protected throughout training.
- Major design choices should be supported by measurable evidence rather than intuition alone.

## Progressive Scaling Strategy

Training a large model from scratch is expensive, so V5 uses progressive scaling. Smaller models are trained first, and their learned representations are used to initialize larger ones.

| Stage | Model size | Approx. tokens | Primary objective |
| --- | --- | --- | --- |
| Initial foundation | 1B | 20B | Learn language structure and basic knowledge |
| Intermediate growth | 3B | 60B | Improve multilingual and programming ability |
| Advanced growth | 8B | 200B | Introduce reasoning and scientific knowledge |
| Production model | ~40B | 8T | Full capability integration |

Each stage builds on the knowledge acquired by the previous one instead of starting from scratch.

## Capability Allocation

The training corpus is divided into capability groups. These allocations are treated as initial hypotheses and may be updated after proxy experiments.

- General language: 30%
- Programming: 18%
- Mathematics and science: 14%
- Multilingual knowledge: 10%
- Indic languages: 10%
- Long context: 8%
- Agentic behaviour: 5%
- Logical reasoning: 5%

These shares are meant to preserve balanced capability growth while protecting important but scarce lanes.

## Indic Language Strategy

Supporting Indian languages is a core objective of V5. Rather than treating Indic data as a single undifferentiated pool, it is split by quality tier:

- Verified native content: 40%
- Verified translations: 25%
- Filtered web content: 20%
- Synthetic generation: 15%

This strategy keeps the highest-quality Indic data dominant while still allowing broader coverage and gap-filling through translation and synthesis.

## Protected Capabilities

Some capabilities have limited available data but remain essential throughout training. To prevent them from disappearing during adaptive sampling, minimum allocation floors are defined:

- Indic languages: 8%
- Programming: 12%
- Mathematics: 10%
- Agentic behaviour: 5%
- Logical reasoning: 5%

## Curriculum Learning Strategy

Curriculum learning is used to introduce knowledge gradually. The model first learns simple language understanding before more complex reasoning, long-context, and tool-use tasks are introduced.

### Phase 1: Language foundation
Focus on grammar, vocabulary, reading comprehension, and general knowledge.

### Phase 2: Capability expansion
Add programming, scientific, multilingual, and verified Indic data.

### Phase 3: Advanced reasoning
Introduce mathematical reasoning, scientific problem solving, logical deduction, and multi-step planning.

### Phase 4: Capability refinement
Add long-context documents, agentic workflows, tool-use traces, and high-quality reasoning examples.

## Difficulty and Reasoning-Length Bands

Training examples are organized into difficulty bands:

- Easy: translation, basic summarization, entity recognition, simple QA.
- Medium: programming exercises, multi-hop QA, code explanation, short logical reasoning.
- Hard: mathematical proofs, algorithm design, scientific analysis, research summarization.
- Expert: long reasoning chains, agentic workflows, multi-document synthesis, tool orchestration.

Reasoning-length bands are also defined:

- Short: single-step reasoning with immediate answers.
- Medium: multiple logical steps before reaching a solution.
- Long: extended reasoning chains involving planning or verification.
- Extended: complex reasoning spanning many tokens and requiring long-horizon planning.

## Annealing Strategy

The highest-quality training data is not consumed immediately. Instead, a reserve of premium samples is held back for later stages of training.

This reserve includes:

- Verified educational documents
- High-quality programming repositories
- Carefully validated reasoning traces
- Premium multilingual datasets
- High-confidence Indic resources

This late-stage exposure improves utilization of expensive data, supports convergence, and helps preserve strong final performance.

## Evaluation Benchmarks

Each capability is evaluated using appropriate benchmarks:

- Language: MMLU
- Programming: HumanEval
- Mathematics: GSM8K, MATH
- Scientific reasoning: GPQA
- Multilingual: FLORES
- Indic languages: IndicBench
- Agentic behaviour: GAIA, BFCL

## Experimental Validation Strategy

Before committing to full-scale training, V5 uses small proxy runs to test important hypotheses.

### Proxy experiment 1: capability allocation
Test whether the proposed mix improves language, programming, and reasoning together without harming general fluency.

### Proxy experiment 2: curriculum evaluation
Compare uniform training against progressive curriculum scheduling.

### Proxy experiment 3: Indic data strategy
Compare several verified/translated/synthetic mixes to find the best balance for multilingual quality and factual reliability.

The plan is accepted only if the proxy results show clear gains or acceptable tradeoffs relative to the baseline.

## Data Quality Pipeline

Every document passes through a validation pipeline before entering the training corpus:

1. License verification
2. Language detection
3. Quality filtering
4. Deduplication
5. Benchmark contamination check
6. Approval for training

## Risk Assessment

The main risks include:

- Excess synthetic data reducing factual quality
- Insufficient Indic resources harming multilingual capability
- Benchmark contamination inflating evaluation scores
- Poor curriculum design causing slower convergence
- Data imbalance introducing capability bias

These risks are mitigated through protected allocations, explicit quality filtering, and continuous evaluation.

## Ethical Data Usage

Every dataset included in V5 should have:

- A clearly identifiable source
- Appropriate usage permission
- Respect for licensing requirements
- Removal of sensitive personal information where needed
- Transparent documentation of origin

## Summary

The V5 pre-training strategy treats the corpus as an engineered system rather than a random collection of documents. By combining capability-aware allocation, curriculum learning, protected floors, annealing, and proxy-based validation, the plan aims to produce a balanced model that performs well across language, reasoning, programming, multilingual understanding, and agentic tasks.
