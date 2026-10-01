"""Import-time and startup behaviour, checked in clean subprocesses."""

import os
import subprocess
import sys

from conftest import AGENT_DIR


def _run(code_or_args, env_extra=None, module=False):
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith(("JWT_", "MUSE_", "DATABASE_", "LANGFUSE_", "DEEPINFRA_", "AI_AGENT_"))
    }
    env.update(env_extra or {})
    args = [sys.executable, *code_or_args] if module else [sys.executable, "-c", code_or_args]
    return subprocess.run(args, cwd=AGENT_DIR, env=env, capture_output=True, text=True, timeout=120)


def test_import_has_no_side_effects_with_empty_env():
    # No config error, no Langfuse client (hence no network) at import time.
    result = _run(
        "import sys, main, observability, echo_graph, echo_agent, db, migrate; "
        "assert 'langfuse' not in sys.modules, 'langfuse imported at import time'; print('ok')",
        env_extra={"LANGFUSE_PUBLIC_KEY": "pk", "LANGFUSE_SECRET_KEY": "sk", "LANGFUSE_BASE_URL": "http://127.0.0.1:1"},
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "ok"


def test_uvicorn_factory_with_bad_env_exits_cleanly():
    result = _run(["-m", "uvicorn", "main:create_app", "--factory", "--port", "0"], module=True)
    assert result.returncode == 1
    assert "ai-agent startup error: invalid ai-agent configuration" in result.stderr
    assert "JWT_SIGNING_KEY is unset" in result.stderr
    assert "Traceback" not in result.stderr


def test_migrate_cli_with_bad_env_exits_cleanly():
    result = _run(["migrate.py"], module=True)
    assert result.returncode == 2
    assert "migrate: configuration error" in result.stderr
    assert "Traceback" not in result.stderr
