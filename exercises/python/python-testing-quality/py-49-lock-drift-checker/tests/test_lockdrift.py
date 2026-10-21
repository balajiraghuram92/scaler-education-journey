import pytest

from lockdrift import bump, find_drift, normalize, parse_release, satisfies, split_requirement

PYPROJECT = """
[project]
name = "gateway"
version = "0.1.0"
dependencies = ["httpx>=0.27,<1", "Pydantic[email]~=2.8", "tenacity"]

[dependency-groups]
dev = ["pytest>=8", {include-group = "lint"}]
lint = ["ruff==0.12.0"]
"""

LOCK = """
version = 1

[[package]]
name = "httpx"
version = "0.28.1"

[[package]]
name = "pydantic"
version = "2.11.3"

[[package]]
name = "tenacity"
version = "9.0.0"

[[package]]
name = "pytest"
version = "8.3.2"

[[package]]
name = "ruff"
version = "0.12.0"
"""


@pytest.mark.parametrize(
    ("version", "specifier", "expected"),
    [
        pytest.param("0.28.1", ">=0.27,<1", True, id="range-ok"),
        pytest.param("1.0.0", ">=0.27,<1", False, id="upper-bound-excl"),
        pytest.param("0.10.0", ">=0.9", True, id="numeric-not-lexicographic"),
        pytest.param("0.9.0", ">0.10.0", False, id="numeric-greater"),
        pytest.param("1.2", "==1.2.0", True, id="zero-padding"),
        pytest.param("2.9.1", "~=2.8", True, id="compatible-release"),
        pytest.param("3.0.0", "~=2.8", False, id="compatible-release-major"),
        pytest.param("2.7.9", "~=2.8", False, id="compatible-release-too-low"),
        pytest.param("2.8.5", "~=2.8.1", True, id="compatible-patch"),
        pytest.param("2.9.0", "~=2.8.1", False, id="compatible-patch-minor"),
        pytest.param("1.0.0", "!=1.0.0", False, id="not-equal"),
        pytest.param("1.0.0", "<=1.0", True, id="less-or-equal-padded"),
        pytest.param("5.0.0", "", True, id="empty-specifier"),
    ],
)
def test_satisfies(version, specifier, expected):
    assert satisfies(version, specifier) is expected, f"satisfies({version!r}, {specifier!r})"


def test_parse_release_and_normalize():
    assert parse_release("1.2.3") == (1, 2, 3)
    assert parse_release("10") == (10,)
    assert normalize("My_Cool.Pkg") == "my-cool-pkg"


@pytest.mark.parametrize("bad", ["1.0rc1", "1.0.post1", "v1.0", ""])
def test_prerelease_and_junk_versions_are_rejected(bad):
    with pytest.raises(ValueError):
        parse_release(bad)
    with pytest.raises(ValueError):
        satisfies(bad, ">=1")


def test_unsupported_clause_rejected():
    with pytest.raises(ValueError, match="unsupported specifier"):
        satisfies("1.0", "=>1.0")


def test_split_requirement_handles_extras_and_markers():
    assert split_requirement("Pydantic[email]~=2.8") == ("pydantic", "~=2.8")
    assert split_requirement('uvloop>=0.19; sys_platform != "win32"') == ("uvloop", ">=0.19")
    assert split_requirement("tenacity") == ("tenacity", "")


def test_no_drift():
    assert find_drift(PYPROJECT, LOCK) == []


def test_drift_detects_missing_and_violating_entries():
    stale_lock = LOCK.replace('name = "tenacity"\nversion = "9.0.0"\n\n[[package]]\n', "")
    stale_lock = stale_lock.replace('version = "0.28.1"', 'version = "1.0.0"')
    assert find_drift(PYPROJECT, stale_lock) == [
        "httpx: locked 1.0.0 violates '>=0.27,<1'",
        "tenacity: missing from lock",
    ]


def test_drift_covers_dependency_groups_and_normalised_names():
    lock = LOCK.replace('version = "0.12.0"', 'version = "0.13.0"').replace('name = "pytest"', 'name = "PyTest"')
    assert find_drift(PYPROJECT, lock) == ["ruff: locked 0.13.0 violates '==0.12.0'"], (
        "group dependencies must be checked, include-group tables skipped, names normalised"
    )


@pytest.mark.parametrize(
    ("version", "part", "expected"),
    [
        ("1.4.9", "patch", "1.4.10"),
        ("1.4.9", "minor", "1.5.0"),
        ("1.4.9", "major", "2.0.0"),
    ],
)
def test_bump(version, part, expected):
    assert bump(version, part) == expected
