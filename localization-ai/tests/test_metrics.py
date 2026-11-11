from app.evals import metrics


def test_extract_placeholders():
    assert metrics.extract_placeholders("Speed {speed} in {count} m") == ["{speed}", "{count}"]
    assert metrics.extract_placeholders("no placeholders") == []
    assert metrics.extract_placeholders("") == []
    assert metrics.extract_placeholders(None) == []
    assert metrics.extract_placeholders("{count} {count}") == ["{count}", "{count}"]


def test_placeholder_preserved_ok():
    assert metrics.placeholder_preserved_ok("A {count} B", "X {count} Y") is True
    # Order does not matter, multiset does.
    assert metrics.placeholder_preserved_ok("A {count} {speed}", "X {speed} {count}") is True
    assert metrics.placeholder_preserved_ok("A {count}", "X") is False
    assert metrics.placeholder_preserved_ok("A {count}", "X {count} {count}") is False
    assert metrics.placeholder_preserved_ok("A {count}", "X {speed}") is False
    # Mangled braces count as missing.
    assert metrics.placeholder_preserved_ok("A {count}", "X count") is False


def test_placeholder_preserved_none_when_source_has_none():
    assert metrics.placeholder_preserved_ok("plain", "anything") is None
    assert metrics.placeholder_preserved_ok("plain", "{count}") is None
    assert metrics.placeholder_preserved_ok("", "") is None


def test_applicable_glossary_terms():
    terms = [("HUD", "HUD"), ("Turn left", "Links abbiegen")]
    assert metrics.applicable_glossary_terms("Turn left ahead", terms) == [("Turn left", "Links abbiegen")]
    assert metrics.applicable_glossary_terms("HUD brightness", terms) == [("HUD", "HUD")]
    assert metrics.applicable_glossary_terms("Cabin temperature", terms) == []
    assert metrics.applicable_glossary_terms(None, terms) == []
    assert metrics.applicable_glossary_terms("Turn left", []) == []


def test_glossary_adherence_ok():
    terms = [("Turn left", "Links abbiegen")]
    assert metrics.glossary_adherence_ok("Turn left", "Links abbiegen", terms) is True
    assert metrics.glossary_adherence_ok("Turn left", "Turn left", terms) is False
    # Case-sensitive: the approved term must appear exactly.
    assert metrics.glossary_adherence_ok("Turn left", "links abbiegen", terms) is False
    # Every applicable term must appear.
    two = [("HUD", "HUD"), ("Turn left", "Links abbiegen")]
    assert metrics.glossary_adherence_ok("HUD: Turn left", "HUD: Links abbiegen", two) is True
    assert metrics.glossary_adherence_ok("HUD: Turn left", "HUD: Turn left", two) is False


def test_glossary_adherence_none_when_nothing_applies():
    terms = [("HUD", "HUD")]
    assert metrics.glossary_adherence_ok("Cabin temperature", "Innentemperatur", terms) is None
    assert metrics.glossary_adherence_ok("HUD on", "HUD an", []) is None


def test_exact_and_normalized_match():
    assert metrics.exact_match("Links abbiegen", "Links abbiegen") is True
    assert metrics.exact_match("Links abbiegen", "links abbiegen") is False
    assert metrics.normalized_match("  Links   abbiegen ", "links ABBIEGEN") is True
    assert metrics.normalized_match("Links abbiegen", "Rechts abbiegen") is False
    assert metrics.exact_match(None, "") is True


def test_rate():
    assert metrics.rate([True, True, True, True]) == 1.0
    assert metrics.rate([True, False]) == 0.5
    assert metrics.rate([False, False]) == 0.0
    # None flags are excluded, not counted as passes.
    assert metrics.rate([True, None]) == 1.0
    assert metrics.rate([None, None]) is None
    assert metrics.rate([]) is None


def test_mean():
    assert metrics.mean([1, 2, 3]) == 2.0
    assert metrics.mean([0, 0]) == 0.0
    assert metrics.mean([2.0, None]) == 2.0
    assert metrics.mean([None, None]) is None
    assert metrics.mean([]) is None


def test_total():
    assert metrics.total([1, 2.5, None]) == 3.5
    assert metrics.total([]) == 0.0
    assert metrics.total([None]) == 0.0
