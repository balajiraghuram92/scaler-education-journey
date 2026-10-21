from importgraph import build_import_graph, find_cycles

SOURCES = {
    "gw": "",
    "gw.config": "from gw.providers import NAMES\nSETTINGS = 1",
    "gw.providers": "from gw.config import SETTINGS\nNAMES = ['a']",
    "gw.util": "VALUE = 1",
    "gw.core": "from . import util\nfrom .util import VALUE\nimport json\n",
    "gw.cli": "import gw.core\nfrom gw import config",
}


def test_graph_resolves_absolute_and_relative_imports_and_ignores_external() -> None:
    graph = build_import_graph(SOURCES)
    assert graph["gw.config"] == {"gw.providers"}
    assert graph["gw.providers"] == {"gw.config"}
    assert graph["gw.core"] == {"gw.util"}  # `json` is not a project module
    assert graph["gw.cli"] == {"gw.core", "gw.config"}


def test_cycles_are_reported_as_sorted_components() -> None:
    graph = build_import_graph(SOURCES)
    assert find_cycles(graph) == [["gw.config", "gw.providers"]]


def test_deferred_and_type_checking_imports_do_not_create_edges() -> None:
    sources = {
        "a": "from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    import b\n",
        "b": "import a\n\ndef f():\n    import a\n",
    }
    graph = build_import_graph(sources)
    assert graph["a"] == set()
    assert graph["b"] == {"a"}
    assert find_cycles(graph) == []


def test_imports_inside_try_and_if_blocks_count() -> None:
    sources = {
        "x": "try:\n    import y\nexcept ImportError:\n    y = None\n",
        "y": "import x\n",
    }
    assert find_cycles(build_import_graph(sources)) == [["x", "y"]]


def test_relative_import_beyond_top_level_is_ignored() -> None:
    sources = {"pkg": "", "pkg.m": "from ..outside import z"}
    assert build_import_graph(sources)["pkg.m"] == set()


def test_package_init_relative_imports() -> None:
    sources = {"pkg": "from . import a", "pkg.a": "import pkg"}
    graph = build_import_graph(sources)
    assert graph["pkg"] == {"pkg.a"}
    assert find_cycles(graph) == [["pkg", "pkg.a"]]


def test_three_module_cycle_and_self_import() -> None:
    sources = {
        "a": "import b",
        "b": "import c",
        "c": "import a\nimport c",
        "d": "import d",
    }
    assert find_cycles(build_import_graph(sources)) == [["a", "b", "c"]]


def test_dotted_imports_use_the_longest_known_module_prefix() -> None:
    sources = {
        "app": "",
        "app.models": "",
        "app.models.user": "",
        "main": (
            "import app.models.user.Thing\n"
            "from app import models\n"
            "from app.models import user, NOT_A_MODULE\n"
        ),
    }
    assert build_import_graph(sources)["main"] == {"app.models.user", "app.models"}


def test_multi_dot_relative_imports() -> None:
    sources = {
        "pkg": "",
        "pkg.sub": "",
        "pkg.sub.deep": "from .. import sibling\nfrom ..sibling import X\nfrom ... import nope\n",
        "pkg.sibling": "X = 1",
    }
    assert build_import_graph(sources)["pkg.sub.deep"] == {"pkg.sibling"}


def test_every_module_is_a_node_and_class_bodies_and_else_branches_count() -> None:
    sources = {
        "a": "class K:\n    import b\n",
        "b": "import a\n",
        "c": "from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    pass\nelse:\n    import b\n",
        "d": "async def f():\n    import a\n",
    }
    graph = build_import_graph(sources)
    assert set(graph) == {"a", "b", "c", "d"}, "modules without edges must still be graph keys"
    assert graph["a"] == {"b"} and graph["c"] == {"b"} and graph["d"] == set()
    assert find_cycles(graph) == [["a", "b"]]
