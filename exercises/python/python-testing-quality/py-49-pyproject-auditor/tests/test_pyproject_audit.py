import dataclasses
import tomllib
from pathlib import Path

import pytest

from pyproject_audit import Issue, audit, normalize, requirement_name

GOOD = """
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "llm-gateway"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["httpx>=0.27,<1", "pydantic>=2.8"]

[project.scripts]
gateway = "llm_gateway.cli:main"
"""


def make_project(root: Path, pyproject: str, *, with_package: bool = True) -> Path:
    (root / "pyproject.toml").write_text(pyproject, encoding="utf-8")
    if with_package:
        pkg = root / "src" / "llm_gateway"
        pkg.mkdir(parents=True)
        (pkg / "__init__.py").write_text("", encoding="utf-8")
    return root


def codes(issues):
    return [i.code for i in issues]


def test_clean_project_has_no_issues(tmp_path):
    assert audit(make_project(tmp_path, GOOD)) == [], "a clean project must return an empty list"


def test_missing_file_returns_only_pp001(tmp_path):
    assert codes(audit(tmp_path)) == ["PP001"]


def test_missing_build_system_and_requires_python(tmp_path):
    text = '[project]\nname = "llm-gateway"\nversion = "0.1.0"\n'
    assert codes(audit(make_project(tmp_path, text))) == ["PP002", "PP003"]


def test_dev_tools_in_runtime_dependencies(tmp_path):
    text = GOOD.replace('"pydantic>=2.8"', '"pydantic>=2.8", "PyTest[extra]>=8", "ruff", "pytest-cov"')
    issues = audit(make_project(tmp_path, text))
    assert codes(issues) == ["PP004", "PP004"], "one PP004 per dev tool; pytest-cov is not pytest"
    assert any("ruff" in i.message for i in issues)
    assert any("PyTest[extra]" in i.message for i in issues)


def test_version_must_be_static_xor_dynamic(tmp_path):
    both = GOOD.replace('version = "0.1.0"', 'version = "0.1.0"\ndynamic = ["version"]')
    neither = GOOD.replace('version = "0.1.0"\n', "")
    dynamic_only = neither.replace("requires-python", 'dynamic = ["version"]\nrequires-python')
    cases = {"a": (both, ["PP005"]), "b": (neither, ["PP006"]), "c": (dynamic_only, [])}
    for name, (text, expected) in cases.items():
        root = tmp_path / name
        root.mkdir()
        assert codes(audit(make_project(root, text))) == expected, f"case {name}"


@pytest.mark.parametrize("target", ["no_colon", "pkg.mod:", ":func", "pkg-mod:main"])
def test_bad_script_targets(tmp_path, target):
    text = GOOD.replace("llm_gateway.cli:main", target)
    assert codes(audit(make_project(tmp_path, text))) == ["PP007"]


def test_flat_layout_is_reported_and_name_is_normalised(tmp_path):
    issues = audit(make_project(tmp_path, GOOD, with_package=False))
    assert codes(issues) == ["PP008"]
    assert "src/llm_gateway/__init__.py" in issues[0].message
    dotted = tmp_path / "dotted"
    dotted.mkdir()
    text = GOOD.replace('name = "llm-gateway"', 'name = "My.Cool-Pkg"')
    (dotted / "pyproject.toml").write_text(text, encoding="utf-8")
    pkg = dotted / "src" / "my_cool_pkg"
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    assert audit(dotted) == [], "package directory is the normalised name with - replaced by _"


def test_invalid_toml_propagates(tmp_path):
    with pytest.raises(tomllib.TOMLDecodeError):
        audit(make_project(tmp_path, "[project]\n[project]\n"))


def test_name_helpers():
    assert normalize("My_Cool.Pkg") == "my-cool-pkg"
    assert normalize("a--b__c..d") == "a-b-c-d"
    assert requirement_name('Pydantic[email]>=2; python_version >= "3.12"') == "pydantic"
    assert requirement_name("httpx") == "httpx"
    with pytest.raises(ValueError):
        requirement_name(">=1.0")


def test_issues_are_frozen_orderable_and_results_sorted(tmp_path):
    issue = Issue("PP001", "x")
    with pytest.raises(dataclasses.FrozenInstanceError):
        issue.code = "PP002"
    assert Issue("PP001", "b") < Issue("PP002", "a")
    text = '[project]\nname = "llm-gateway"\ndependencies = ["ruff"]\n'
    found = codes(audit(make_project(tmp_path, text, with_package=False)))
    assert found == sorted(found) == ["PP002", "PP003", "PP004", "PP006", "PP008"]
