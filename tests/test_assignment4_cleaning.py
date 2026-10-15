import importlib.util
from collections import Counter
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "S4-data-cleaning-deduplication" / "clean_dataset.py"
SPEC = importlib.util.spec_from_file_location("assignment4_clean_dataset", MODULE_PATH)
cleaning = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cleaning)


def test_normalization_preserves_indic_joiners_and_removes_noise():
    counters = Counter()
    text = cleaning.normalize_text("A &amp; B\u200b\ufeff\u202e क्\u200dष \ufffd", counters)

    assert text == "A & B क्\u200dष"
    assert counters["html_entities_decoded"] == 1
    assert counters["invisible_or_control_chars_removed"] == 4
    assert counters["indic_joiners_preserved"] == 1


def test_clean_rows_masks_pii_and_deduplicates_deterministically():
    content = (
        "This carefully written educational answer explains a useful topic in detail. "
        "Contact learner@example.org or call +1 (415) 555-0132. "
        "The server address is 192.168.1.24. "
    ) * 3
    messages = [
        {"role": "user", "content": "Please explain the topic in a useful way."},
        {"role": "assistant", "content": content},
    ]
    report = cleaning.clean_rows([{"messages": messages}, {"messages": messages}])

    assert report["source_rows"] == 2
    assert report["accepted_rows"] == 1
    assert report["exact_duplicates_removed"] == 1
    assert report["cleaning_counts"]["emails_masked"] == 6
    assert report["cleaning_counts"]["phones_masked"] == 6
    assert report["cleaning_counts"]["ip_addresses_masked"] == 6
    assert "learner@example.org" not in str(report["cleaned_conversations"])