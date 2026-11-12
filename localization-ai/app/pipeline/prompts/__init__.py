"""Prompt templates (plain text, string.Template ``$name`` vars) and versions.

One file per prompt. The version string is returned on every eval run so
results can be tied to the prompt that produced them. (Persisting it on the
EvalRun row awaits a prompt-version column that LA1 did not add; see
PROGRESS.md.)
"""

from pathlib import Path
from string import Template

MT_OPTIMIZE_PROMPT_VERSION = "mt-optimize-v1"
QPS_PROMPT_VERSION = "qps_judge_v2"
# qps_judge_v1.txt stays on disk and loadable by filename (render takes the
# template filename, not a version), so the eval harness can still run a v1
# configuration by rendering it directly.

PROMPTS_DIR = Path(__file__).resolve().parent


def load_prompt(filename: str) -> Template:
    return Template((PROMPTS_DIR / filename).read_text(encoding="utf-8"))


def render(filename: str, **kwargs: str) -> str:
    return load_prompt(filename).substitute(kwargs)
