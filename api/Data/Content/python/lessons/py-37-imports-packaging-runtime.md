# The Import System, Packages and Runtime Environments

"Works on my machine" in Python is almost always an import or environment problem: a module shadowed by a file in the working directory, a circular import that only fails in one entry order, a console script that cannot find its package, or a deployment built from a different virtual environment than the one you tested. Senior engineers can explain exactly how a name becomes a module and where Python looks. That knowledge turns these incidents from hours of guessing into minutes of diagnosis.

## Concepts Covered

### What `import` does: `sys.modules`, finders and loaders

`import x` runs a fixed protocol. First Python checks the cache `sys.modules`; if `x` is there, that module object is returned immediately, which is why importing twice runs the module body once. Otherwise it asks each **finder** in `sys.meta_path` to produce a **spec** (a `ModuleSpec`: name, loader, origin, and `submodule_search_locations` for packages). The default finders are `BuiltinImporter`, `FrozenImporter` and `PathFinder`, and `PathFinder` searches the entries of `sys.path` using per-directory path hooks. The spec's **loader** then creates the module object, registers it in `sys.modules` **before** executing the module body, and runs the body in the module's namespace.

```python
import sys, importlib.util

print([f.__name__ for f in sys.meta_path])
spec = importlib.util.find_spec("json")
print(spec.name, type(spec.loader).__name__, spec.submodule_search_locations is not None)

import json
print(sys.modules["json"] is json, importlib.util.find_spec("nothing_here"))
```

```text
['BuiltinImporter', 'FrozenImporter', 'PathFinder']
json SourceFileLoader True
True None
```

The fact that registration happens **before** execution is the root cause of circular-import errors, as we will see. `importlib.reload(module)` re-executes a module body in place but does not update names other modules bound with `from m import name`, so it is a debugging aid, not a deployment strategy.

### `sys.path`, shadowing and how scripts differ from `-m`

`sys.path` is the ordered list of places `PathFinder` searches. It is built from: the script's directory (or the current directory for `-m` and the interactive prompt), `PYTHONPATH`, the standard library, and the `site-packages` directory of the active environment (plus `.pth` files processed by `site`). Earlier entries win, so a file named `random.py` or `json.py` in your project directory **shadows** the standard library, and the failure message mentions "partially initialized module" or an unexpected attribute error.

The way you start Python changes `sys.path[0]`: `python script.py` puts the script's directory first, while `python -m package.module` puts the current directory first and runs the module as `__main__` with its package context intact. That is why relative imports work under `-m` but fail when you run the same file as a script with "attempted relative import with no known parent package". Prefer `python -m pkg.cli` over running files by path. `python -m pkg` runs `pkg/__main__.py`, and `python -m pytest` uses the current interpreter's pytest instead of whichever `pytest` is first on `PATH`.

> **Pitfall:** Naming your module after a stdlib or third-party module (`email.py`, `types.py`, `logging.py`, `openai.py`) shadows it. Use `python -X importtime -c "import yourpkg"` and `python -c "import x; print(x.__file__)"` to see what was actually imported.

### Packages, namespace packages and relative imports

A **regular package** is a directory with an `__init__.py`; the file runs when the package is first imported, and it defines the package's public face (re-exports and `__all__`). A **namespace package** (PEP 420) is a directory *without* `__init__.py`; its `__path__` is assembled from every matching directory on `sys.path`, so several distributions can contribute subpackages to the same top-level name (this is how many `company.*` plugin ecosystems are laid out).

```python
import sys, tempfile, os

d1, d2 = tempfile.mkdtemp(), tempfile.mkdtemp()
os.mkdir(os.path.join(d1, "nsdemo"))
os.mkdir(os.path.join(d2, "nsdemo"))
sys.path[:0] = [d1, d2]

import nsdemo
print(type(nsdemo.__path__).__name__, len(list(nsdemo.__path__)), getattr(nsdemo, "__file__", None))
```

```text
_NamespacePath 2 None
```

Inside a package, **relative imports** (`from .util import VALUE`, `from . import util`, `from ..shared import config`) resolve against the module's `__package__`. They keep a package relocatable but require that the module is imported as part of its package, and going above the top-level package raises `ImportError: attempted relative import beyond top-level package`. Absolute imports from the package root are easier to grep and to move around; many teams standardise on absolute imports and use relative ones only inside a small subpackage. A `src/` layout (`src/yourpkg/...`) prevents tests from importing the working-tree copy by accident, so they exercise the installed package.

### Circular imports: diagnosis and fixes

When module A imports B while B is importing A, B receives A's **partially initialised** module object from `sys.modules`. A plain `import a` succeeds (you get the module object, still being filled in), but `from a import name` fails if `name` has not been defined yet.

```python
# gw_a.py
from gw_b import b_value      # starts importing gw_b, which immediately wants gw_a
a_value = 1

# gw_b.py
from gw_a import a_value      # gw_a is in sys.modules but 'a_value' does not exist yet
b_value = 2
```

```text
ImportError: cannot import name 'a_value' from partially initialized module 'gw_a' (most likely due to a circular import)
```

It often fails only for one entry point, such as running the test for `gw_b` first, which is what makes it flaky in CI. The fixes, in order of preference:

1. **Break the cycle** by extracting the shared piece into a third module that both import (the dependency direction should be one-way: a layered design).
2. **Import the module, not the name:** `import gw_b` at the top and use `gw_b.b_value` inside functions, so attribute access happens after both modules finish loading.
3. **Import inside the function** that needs it (deferred import), which also helps start-up time for heavy dependencies:

```python
# gw_a.py
a_value = 1

def total():
    from gw_b import b_value     # resolved at call time, when both modules are fully loaded
    return a_value + b_value
```

4. **`typing.TYPE_CHECKING`** for imports needed only by annotations, combined with `from __future__ import annotations` (or string annotations), so the import never runs at runtime.

> **Interview tip:** Say that a cycle is a design smell first and a mechanical problem second. Name the root cause (the module is registered before its body finishes) and propose extracting a shared module before reaching for local imports.

### `__main__`, entry points and plugin discovery

When a file is run as a program its `__name__` is `"__main__"`, so the guard `if __name__ == "__main__": main()` keeps imports side-effect free. For installed tools use **entry points** declared in `pyproject.toml`; the installer generates an executable that imports and calls your function:

```toml
[project]
name = "gateway"
version = "0.1.0"
requires-python = ">=3.12"

[project.scripts]
gw = "gateway.cli:main"

[project.entry-points."gateway.providers"]
openai = "gateway.providers.openai:OpenAIProvider"
local = "gateway.providers.local:LocalProvider"
```

The second table is a **plugin group**. At run time, `importlib.metadata.entry_points(group="gateway.providers")` yields entries whose `.load()` imports the target, so third-party packages can register providers without you editing any registry. You can inspect the same mechanism on any environment:

```python
from importlib.metadata import entry_points

for ep in entry_points(group="console_scripts"):
    print(ep.name, ep.value)
```

```text
pip pip._internal.cli.main:main
pip3 pip._internal.cli.main:main
```

### Virtual environments and `site-packages`

A virtual environment is a directory with its own `site-packages`, a `pyvenv.cfg`, and a launcher that sets `sys.prefix` apart from `sys.base_prefix`. Activation merely changes `PATH`; what matters is which `python` runs. Inside a venv, `sys.prefix != sys.base_prefix`, and `sysconfig.get_paths()["purelib"]` shows where packages install.

```bash
python -m venv .venv
.venv/bin/python -m pip install -e .         # editable install of your project
.venv/bin/python -c "import sys; print(sys.prefix != sys.base_prefix)"
.venv/bin/python -m pip freeze > requirements.txt
```

Always call `python -m pip` so pip installs into the interpreter you mean, never use `sudo pip`, and commit a lock or pinned requirements file so builds are reproducible.

## Practical Backend Scenario

A FastAPI gateway passes locally but crashes at start-up in CI with `ImportError: cannot import name 'Settings' from partially initialized module 'gateway.config'`. `gateway.config` imports `gateway.providers` to validate provider names, and `gateway.providers` imports `Settings` from `gateway.config` to read keys. Locally the app starts via `gateway.main`, which imports `config` first; the CI test imports `gateway.providers` first, entering the cycle from the other side. The fix is to move the provider-name constants into `gateway/constants.py`, which both modules import, and to load provider classes through the `gateway.providers` entry-point group instead of importing them from `config`.

## Practice Loop

1. Print `sys.meta_path`, `sys.path` and `importlib.util.find_spec("yourpkg")` inside your project's venv, and explain each entry.
2. Create `gw_a.py` and `gw_b.py` with the circular `from ... import` pattern, run `python -c "import gw_a"` and `python -c "import gw_b"`, and record both outcomes. Fix it three different ways.
3. Make a small package with an absolute and a relative import. Run it with `python -m` and then as `python path/to/file.py` and explain the difference in `sys.path[0]` and the relative-import error.
4. Add a `[project.scripts]` entry and a plugin entry-point group to a `pyproject.toml`, install with `pip install -e .`, and call `entry_points(group=...)` to load a plugin.

## Evidence of Understanding

- I can describe the steps of an import and the roles of `sys.modules`, finders, loaders and specs.
- I can explain why a module is registered in `sys.modules` before it executes, and why that causes circular-import errors.
- I can diagnose shadowing and the difference between running a script and `python -m`.
- I can explain namespace versus regular packages, and relative versus absolute imports.
- I can configure `console_scripts` and plugin entry points and load them with `importlib.metadata`.
- I can explain what a venv is and how to make an environment reproducible.

## Interview Questions to Rehearse

### Q: Walk me through what happens on `import a.b`.

Python imports `a` first (checking `sys.modules`, then finders for a spec, then loading it), then imports `a.b` using `a.__path__` as the search location. Each module is created, put in `sys.modules`, and executed, and `b` is also set as an attribute on `a`. Subsequent imports hit the cache.

### Q: Why does `from a import x` fail in a circular import when `import a` works?

`import a` only needs the module object, which exists in `sys.modules` while it is still executing. `from a import x` needs the attribute `x` to exist at that moment, and it does not if `a` has not reached the line that defines it. Moving the import into a function, importing the module instead, or extracting shared code removes the dependency on timing.

### Q: What is the difference between a regular package and a namespace package?

A regular package has an `__init__.py` and a single location. A namespace package has no `__init__.py`, and its `__path__` is the union of every matching directory on `sys.path`, which lets separate distributions share a top-level name. The cost is no package-level initialization code and some tooling confusion, so use them deliberately for plugin ecosystems.

### Q: How does a console script installed by pip find your code?

The `[project.scripts]` entry maps a command name to `module:function`. The installer writes a small launcher that imports that module in the environment and calls the function. It uses the interpreter of that environment, which is why the right venv matters.

## Common Pitfalls

- Naming local modules after standard-library or installed packages, causing shadowing.
- Running package files as scripts and then adding hacky `sys.path.append` calls instead of using `python -m` or an editable install.
- Circular imports resolved by moving imports around randomly without fixing the dependency direction.
- Using `pip` without knowing which interpreter it belongs to; always use `python -m pip`.
- Unpinned dependencies and no lock file, so two builds of the same commit differ.

## Suggested Extension

Build a tiny plugin loader: a `gateway` package with a `Provider` Protocol and two plugin distributions registered through the `gateway.providers` entry-point group. Discover them with `importlib.metadata`, skip and log plugins that fail to import, and test it in a fresh venv.
