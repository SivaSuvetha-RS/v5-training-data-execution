"""Fetch and clean a deterministic UltraChat SFT sample for Assignment 4."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import html
import json
import re
import unicodedata
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

from datasketch import MinHash, MinHashLSH
from langdetect import DetectorFactory, detect_langs
from langdetect.lang_detect_exception import LangDetectException


DATASET = "HuggingFaceH4/ultrachat_200k"
SPLIT = "train_sft"
SOURCE_REVISION = "8049631c405ae6576f93f445c6b8166f76f5505a"
SOURCE_ROWS = 207_865
PAGE_SIZE = 100
EMAIL = re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
PHONE = re.compile(r"(?<!\w)\+?\d(?:[\s()-]*\d){8,}(?!\w)")
IP_ADDRESS = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
WORD = re.compile(r"\b\w+\b", re.UNICODE)
HTML_ENTITY = re.compile(r"&(?:#[0-9]+|#x[0-9a-fA-F]+|[A-Za-z][A-Za-z0-9]+);")
SHINGLE_WIDTH = 5
MINHASH_PERMUTATIONS = 32
LSH_THRESHOLD = 0.88


def fetch_page(offset: int, length: int) -> list[dict]:
    query = urllib.parse.urlencode(
        {
            "dataset": DATASET,
            "config": "default",
            "split": SPLIT,
            "revision": SOURCE_REVISION,
            "offset": offset,
            "length": length,
        }
    )
    request = urllib.request.Request(
        f"https://datasets-server.huggingface.co/rows?{query}",
        headers={"User-Agent": "assignment-4-data-cleaning/1.0"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.load(response)
    return [item["row"] for item in payload["rows"]]


def fetch_sample(row_count: int) -> list[dict]:
    offsets = list(range(0, row_count, PAGE_SIZE))
    lengths = [min(PAGE_SIZE, row_count - offset) for offset in offsets]
    pages: dict[int, list[dict]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(fetch_page, offset, length): offset
            for offset, length in zip(offsets, lengths)
        }
        for future in concurrent.futures.as_completed(futures):
            pages[futures[future]] = future.result()
    return [row for offset in offsets for row in pages[offset]]


def normalize_text(value: str, counters: Counter) -> str:
    text = unicodedata.normalize("NFC", value)
    counters["html_entities_decoded"] += sum(
        html.unescape(match.group()) != match.group() for match in HTML_ENTITY.finditer(text)
    )
    unescaped = html.unescape(text)
    text = unescaped

    def remove_noise(character: str) -> bool:
        codepoint = ord(character)
        if character == "\ufffd" or character in "\ufeff\u200b":
            return True
        if 0x202A <= codepoint <= 0x202E or 0x2066 <= codepoint <= 0x2069:
            return True
        return unicodedata.category(character) == "Cc" and character not in "\n\t\r"

    cleaned = "".join(character for character in text if not remove_noise(character))
    counters["invisible_or_control_chars_removed"] += len(text) - len(cleaned)
    counters["indic_joiners_preserved"] += sum(cleaned.count(mark) for mark in ("\u200c", "\u200d"))
    return re.sub(r"\s+", " ", cleaned).strip()


def clean_message(value: str, counters: Counter) -> str:
    text = normalize_text(value, counters)
    for label, pattern in (("emails_masked", EMAIL), ("phones_masked", PHONE), ("ip_addresses_masked", IP_ADDRESS)):
        text, count = pattern.subn("[REDACTED]", text)
        counters[label] += count
    return text


def canonicalize(row: dict, counters: Counter) -> list[dict[str, str]]:
    messages = row.get("messages")
    if not isinstance(messages, list):
        counters["invalid_conversation_format"] += 1
        return []

    canonical = []
    for message in messages:
        if not isinstance(message, dict):
            counters["invalid_message_records"] += 1
            continue
        role = str(message.get("role", "")).strip().lower()
        content = message.get("content", "")
        if role not in {"system", "user", "assistant"} or not isinstance(content, str):
            counters["invalid_message_records"] += 1
            continue
        canonical.append({"role": role, "content": clean_message(content, counters)})
    return canonical


def quality_failure(messages: list[dict[str, str]], raw_messages: list[dict]) -> str | None:
    text = " ".join(message["content"] for message in messages)
    words = WORD.findall(text)
    if len(text) < 80 or len(words) < 10:
        return "too_short"
    lines = [
        line.strip()
        for message in raw_messages
        if isinstance(message, dict) and isinstance(message.get("content"), str)
        for line in message["content"].splitlines()
        if line.strip()
    ]
    if lines and 1 - len(set(lines)) / len(lines) > 0.5:
        return "repeated_lines"
    return None


def detect_language(messages: list[dict[str, str]]) -> tuple[str, float]:
    text = " ".join(message["content"] for message in messages)[:4000]
    try:
        guesses = detect_langs(text)
    except LangDetectException:
        return "unknown", 0.0
    return (guesses[0].lang, float(guesses[0].prob)) if guesses else ("unknown", 0.0)


def document_minhash(messages: list[dict[str, str]]) -> MinHash:
    tokens = WORD.findall(" ".join(message["content"].lower() for message in messages))
    shingles = [" ".join(tokens[index : index + SHINGLE_WIDTH]) for index in range(max(0, len(tokens) - SHINGLE_WIDTH + 1))]
    if len(shingles) > 128:
        step = len(shingles) / 128
        shingles = [shingles[int(index * step)] for index in range(128)]
    signature = MinHash(num_perm=MINHASH_PERMUTATIONS, seed=42)
    for shingle in shingles:
        signature.update(shingle.encode("utf-8"))
    return signature


def document_hash(messages: list[dict[str, str]]) -> str:
    canonical = json.dumps(messages, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def clean_rows(rows: list[dict]) -> dict:
    DetectorFactory.seed = 0
    counters: Counter = Counter()
    stats = {
        "source_rows": len(rows),
        "accepted_rows": 0,
        "source_whitespace_tokens": 0,
        "clean_whitespace_tokens": 0,
        "source_characters": 0,
        "clean_characters": 0,
        "messages": 0,
        "source_languages": {},
        "rejected_quality": 0,
        "rejected_language": 0,
        "exact_duplicates_removed": 0,
        "near_duplicates_removed": 0,
        "duplicate_tokens_removed": 0,
        "contamination_canaries_found": 0,
        "strategies_applied": [
            "Structured conversation normalization",
            "Unicode and whitespace cleanup",
            "English language validation",
            "Heuristic quality filtering",
            "Exact and MinHash near-deduplication",
            "Regex PII masking",
            "Canary contamination scan",
            "Deterministic content hashes and provenance",
        ],
        "quality_rejection_reasons": {},
    }
    accepted: list[tuple[str, list[dict[str, str]], int]] = []
    canaries = ("S4-EVAL-CANARY-7f92d1", "S4-HELDOUT-CANARY-b18e42")

    for row in rows:
        raw_messages = row.get("messages") or []
        raw_text = " ".join(
            message.get("content", "")
            for message in raw_messages
            if isinstance(message, dict) and isinstance(message.get("content"), str)
        )
        stats["source_characters"] += len(raw_text)
        stats["source_whitespace_tokens"] += len(raw_text.split())
        messages = canonicalize(row, counters)
        if not messages:
            stats["rejected_quality"] += 1
            continue

        reason = quality_failure(messages, raw_messages)
        if reason:
            stats["rejected_quality"] += 1
            counters[f"quality_{reason}"] += 1
            continue

        language, confidence = detect_language(messages)
        stats["source_languages"][language] = stats["source_languages"].get(language, 0) + 1
        if language != "en" or confidence < 0.55:
            stats["rejected_language"] += 1
            counters["language_low_confidence_or_mismatch"] += 1
            continue

        text = " ".join(message["content"] for message in messages)
        stats["clean_characters"] += len(text)
        stats["clean_whitespace_tokens"] += len(text.split())
        stats["messages"] += len(messages)
        stats["contamination_canaries_found"] += sum(canary in text for canary in canaries)
        accepted.append((document_hash(messages), messages, len(text.split())))

    exact_hashes: set[str] = set()
    unique: list[tuple[str, list[dict[str, str]], int]] = []
    for item in accepted:
        if item[0] in exact_hashes:
            stats["exact_duplicates_removed"] += 1
            stats["duplicate_tokens_removed"] += item[2]
            continue
        exact_hashes.add(item[0])
        unique.append(item)

    index = MinHashLSH(threshold=LSH_THRESHOLD, num_perm=MINHASH_PERMUTATIONS)
    signatures: dict[str, MinHash] = {}
    retained: list[tuple[str, list[dict[str, str]], int]] = []
    for content_hash, messages, token_count in unique:
        signature = document_minhash(messages)
        candidates = index.query(signature)
        if candidates:
            stats["near_duplicates_removed"] += 1
            stats["duplicate_tokens_removed"] += token_count
            continue
        index.insert(content_hash, signature)
        signatures[content_hash] = signature
        retained.append((content_hash, messages, token_count))

    stats["accepted_rows"] = len(retained)
    stats["messages"] = sum(len(messages) for _, messages, _ in retained)
    stats["quality_rejection_reasons"] = dict(sorted(counters.items()))
    stats["clean_whitespace_tokens"] -= stats["duplicate_tokens_removed"]
    stats["clean_characters"] = sum(
        len(" ".join(message["content"] for message in messages))
        for _, messages, _ in retained
    )
    stats["processed_hash"] = hashlib.sha256(
        "".join(content_hash for content_hash, _, _ in retained).encode("ascii")
    ).hexdigest()
    stats["sample_definition"] = f"First {len(rows):,} rows of {SPLIT}; fixed source order; Hugging Face Datasets Server"
    stats["duplicate_hashes_removed"] = stats["near_duplicates_removed"] + stats["exact_duplicates_removed"]
    stats["cleaned_conversations"] = [
        {"content_hash": content_hash, "messages": messages}
        for content_hash, messages, _ in retained
    ]
    stats["cleaning_counts"] = dict(sorted(counters.items()))
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=12_000, help="Rows to fetch from the start of train_sft (default: 12000).")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parent / "artifacts",
        help="Directory for the machine-readable report and optional cleaned JSONL.",
    )
    parser.add_argument("--write-cleaned", action="store_true", help="Also write the cleaned conversations as JSONL.")
    args = parser.parse_args()
    if not 1 <= args.rows <= SOURCE_ROWS:
        parser.error(f"--rows must be between 1 and {SOURCE_ROWS}")

    rows = fetch_sample(args.rows)
    report = clean_rows(rows)
    cleaned = report.pop("cleaned_conversations")
    report["dataset"] = DATASET
    report["split"] = SPLIT
    report["source_rows_in_split"] = SOURCE_ROWS
    report["dataset_license"] = "MIT"
    report["source_revision"] = SOURCE_REVISION
    report["cleaning_script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report["processing_notes"] = [
        "Whitespace-delimited words are a transparent size proxy, not model-tokenizer counts.",
        "The English-only source split is checked with langdetect; this sample does not validate Indic language recall.",
        "The canary scan checks two synthetic canaries, not full benchmark fingerprints.",
        "Name-based PII detection and manually reviewed false-positive assessment are not included.",
        "MinHash LSH uses 5-word shingles, a deterministic 128-shingle cap, 32 permutations, and a 0.88 candidate threshold.",
    ]
    args.output.mkdir(parents=True, exist_ok=True)
    if args.write_cleaned:
        with (args.output / "cleaned.jsonl").open("w", encoding="utf-8") as handle:
            for conversation in cleaned:
                handle.write(json.dumps(conversation, ensure_ascii=False, sort_keys=True) + "\n")
    with (args.output / "stats.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False, sort_keys=True)
        handle.write("\n")
    print(json.dumps({key: value for key, value in report.items() if key != "cleaning_counts"}, indent=2))


if __name__ == "__main__":
    main()