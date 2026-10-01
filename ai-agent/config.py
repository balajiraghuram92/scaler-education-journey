"""Environment configuration for the ai-agent service.

Nothing here runs at import time. Call ``get_settings()`` (cached) or
``load_settings(environ)`` to read and validate the environment. All problems
are collected and raised together as one ``ConfigError`` whose message names
the variables involved but never their values.

Database connection, either shape:
  * ``DATABASE_URL`` (libpq URI or ``key=value`` string). A password inside a
    URI must be percent-encoded (``@`` -> ``%40``, ``:`` -> ``%3A`` ...).
  * ``DATABASE_HOST``, ``DATABASE_NAME``, ``DATABASE_USER``,
    ``DATABASE_PASSWORD`` and optional ``DATABASE_PORT`` (default 5432).
    Values are used verbatim, so any character in the password is safe.
``DATABASE_URL`` wins when both shapes are present.
"""

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from functools import lru_cache

import psycopg
from psycopg.conninfo import conninfo_to_dict, make_conninfo

MIN_JWT_KEY_BYTES = 32  # same floor as api/Program.cs (Auth:JwtSigningKey)

DEFAULT_MUSE_MODEL = "muse-spark-1.3"
DEFAULT_MUSE_BASE_URL = "https://api.meta.ai/v1"

_DB_PART_NAMES = ("DATABASE_HOST", "DATABASE_NAME", "DATABASE_USER", "DATABASE_PASSWORD")
_TRUE_VALUES = {"1", "true", "yes", "on"}


class ConfigError(RuntimeError):
    """Raised when the environment is missing or has invalid settings."""


@dataclass(frozen=True)
class Settings:
    jwt_signing_key: str = field(repr=False)
    muse_api_key: str = field(repr=False)
    database_conninfo: str = field(repr=False)
    jwt_issuer: str = "neuralascent"
    jwt_audience: str = "neuralascent-app"
    jwt_cookie_name: str = "na_auth"
    muse_model: str = DEFAULT_MUSE_MODEL
    muse_base_url: str = DEFAULT_MUSE_BASE_URL
    llm_timeout_seconds: float = 60.0
    deepinfra_api_key: str | None = field(default=None, repr=False)
    langfuse_enabled: bool = False
    enable_docs: bool = False
    rate_limit_per_minute: int = 30


def _get(env: Mapping[str, str], name: str) -> str | None:
    value = env.get(name)
    if value is None:
        return None
    value = value.strip()
    return value or None


def build_database_conninfo(env: Mapping[str, str]) -> str:
    """Return a libpq conninfo string from DATABASE_URL or DATABASE_* parts."""
    url = _get(env, "DATABASE_URL")
    if url:
        invalid = ConfigError(
            "DATABASE_URL is not a valid PostgreSQL connection string "
            "(percent-encode special characters in the password, or use "
            "DATABASE_HOST/NAME/USER/PASSWORD instead)"
        )
        try:
            parts = conninfo_to_dict(url)
        except psycopg.ProgrammingError:
            raise invalid from None  # the driver's message can quote the password
        # libpq accepts some mis-encoded URIs silently, e.g. an unencoded "@" or
        # "/" in the password moves text into host/port/dbname. Catch the usual signs.
        port = str(parts.get("port") or "5432")
        host = str(parts.get("host") or "")
        if not all(p.isdigit() for p in port.split(",")) or "@" in host or not parts.get("dbname"):
            raise invalid
        return url

    missing = [name for name in _DB_PART_NAMES if not _get(env, name)]
    if missing:
        raise ConfigError(
            "database settings missing: set DATABASE_URL, or all of "
            + ", ".join(_DB_PART_NAMES)
            + f" (missing: {', '.join(missing)})"
        )

    port = _get(env, "DATABASE_PORT") or "5432"
    if not port.isdigit():
        raise ConfigError("DATABASE_PORT must be a number")

    # make_conninfo quotes/escapes each value, so @ : / # % ' \ and spaces are safe.
    # The password is read raw (not stripped) so leading/trailing characters survive.
    return make_conninfo(
        host=_get(env, "DATABASE_HOST"),
        port=port,
        dbname=_get(env, "DATABASE_NAME"),
        user=_get(env, "DATABASE_USER"),
        password=env["DATABASE_PASSWORD"],
    )


def _parse_bool(env: Mapping[str, str], name: str, problems: list[str]) -> bool:
    value = _get(env, name)
    if value is None:
        return False
    lowered = value.lower()
    if lowered in _TRUE_VALUES:
        return True
    if lowered in {"0", "false", "no", "off"}:
        return False
    problems.append(f"{name} must be true or false")
    return False


def _parse_number(env, name, default, cast, problems):
    value = _get(env, name)
    if value is None:
        return default
    try:
        parsed = cast(value)
    except ValueError:
        problems.append(f"{name} must be a number")
        return default
    if parsed <= 0:
        problems.append(f"{name} must be greater than zero")
        return default
    return parsed


def load_settings(environ: Mapping[str, str] | None = None) -> Settings:
    """Validate the environment and return Settings, or raise one ConfigError."""
    env = os.environ if environ is None else environ
    problems: list[str] = []

    jwt_key = env.get("JWT_SIGNING_KEY") or ""
    if not jwt_key.strip():
        problems.append("JWT_SIGNING_KEY is unset")
    elif len(jwt_key.encode("utf-8")) < MIN_JWT_KEY_BYTES:
        problems.append(f"JWT_SIGNING_KEY must be at least {MIN_JWT_KEY_BYTES} bytes")

    muse_key = _get(env, "MUSE_AI_API_KEY")
    if not muse_key:
        problems.append("MUSE_AI_API_KEY is unset")

    conninfo = ""
    try:
        conninfo = build_database_conninfo(env)
    except ConfigError as exc:
        problems.append(str(exc))

    enable_docs = _parse_bool(env, "AI_AGENT_ENABLE_DOCS", problems)
    rate_limit = _parse_number(env, "AI_AGENT_RATE_LIMIT_PER_MINUTE", 30, int, problems)
    llm_timeout = _parse_number(env, "LLM_TIMEOUT_SECONDS", 60.0, float, problems)

    if problems:
        raise ConfigError("invalid ai-agent configuration: " + "; ".join(problems))

    return Settings(
        jwt_signing_key=jwt_key,
        muse_api_key=muse_key,
        database_conninfo=conninfo,
        jwt_issuer=_get(env, "JWT_ISSUER") or "neuralascent",
        jwt_audience=_get(env, "JWT_AUDIENCE") or "neuralascent-app",
        jwt_cookie_name=_get(env, "JWT_COOKIE_NAME") or "na_auth",
        muse_model=_get(env, "MUSE_MODEL") or DEFAULT_MUSE_MODEL,
        muse_base_url=_get(env, "MUSE_BASE_URL") or DEFAULT_MUSE_BASE_URL,
        llm_timeout_seconds=llm_timeout,
        deepinfra_api_key=_get(env, "DEEPINFRA_API_KEY"),
        langfuse_enabled=bool(_get(env, "LANGFUSE_PUBLIC_KEY") and _get(env, "LANGFUSE_SECRET_KEY")),
        enable_docs=enable_docs,
        rate_limit_per_minute=rate_limit,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Process-wide settings, validated once on first use."""
    return load_settings()
