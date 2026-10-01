import pytest
from psycopg.conninfo import conninfo_to_dict

import config

SPECIAL_PASSWORD = "p@ss:w/rd#50%' \\x"
GOOD_KEY = "k" * 32


def base_env(**extra):
    env = {"JWT_SIGNING_KEY": GOOD_KEY, "MUSE_AI_API_KEY": "muse-test"}
    env.update(extra)
    return env


def parts_env(password=SPECIAL_PASSWORD, **extra):
    return base_env(
        DATABASE_HOST="database",
        DATABASE_NAME="StudyTrackerDB",
        DATABASE_USER="studyuser",
        DATABASE_PASSWORD=password,
        **extra,
    )


def test_parts_shape_keeps_special_characters_intact():
    settings = config.load_settings(parts_env(DATABASE_PORT="6543"))
    parsed = conninfo_to_dict(settings.database_conninfo)
    assert parsed == {
        "host": "database",
        "port": "6543",
        "dbname": "StudyTrackerDB",
        "user": "studyuser",
        "password": SPECIAL_PASSWORD,
    }


def test_parts_shape_defaults_port_5432():
    parsed = conninfo_to_dict(config.load_settings(parts_env()).database_conninfo)
    assert parsed["port"] == "5432"


def test_url_shape_with_percent_encoded_password():
    url = "postgresql://studyuser:p%40ss%3Aw%2Frd%2350%25@database:5432/StudyTrackerDB"
    parsed = conninfo_to_dict(config.load_settings(base_env(DATABASE_URL=url)).database_conninfo)
    assert parsed["password"] == "p@ss:w/rd#50%"
    assert parsed["dbname"] == "StudyTrackerDB"


def test_url_wins_over_parts():
    url = "postgresql://u:p@urlhost:5432/urldb"
    settings = config.load_settings(parts_env(DATABASE_URL=url))
    assert conninfo_to_dict(settings.database_conninfo)["host"] == "urlhost"


@pytest.mark.parametrize(
    "url",
    [
        "postgresql://u:secretpw@h:notaport/db",  # bad port
        "postgresql://u:secret@pw@h/db",  # unencoded @ in password
        "postgresql://u:secret/pw@h/db",  # unencoded / in password
        "postgresql://u:secretpw50%@h/db",  # unencoded % in password
        "not a url",
    ],
)
def test_malformed_url_is_a_config_error_without_the_value(url):
    with pytest.raises(config.ConfigError) as err:
        config.load_settings(base_env(DATABASE_URL=url))
    assert "DATABASE_URL" in str(err.value)
    assert "secret" not in str(err.value)


def test_missing_everything_lists_names_in_one_error():
    with pytest.raises(config.ConfigError) as err:
        config.load_settings({})
    message = str(err.value)
    for name in ("JWT_SIGNING_KEY", "MUSE_AI_API_KEY", "DATABASE_URL", "DATABASE_PASSWORD"):
        assert name in message


def test_partial_db_parts_names_the_missing_ones():
    env = parts_env()
    del env["DATABASE_PASSWORD"]
    with pytest.raises(config.ConfigError, match="missing: DATABASE_PASSWORD"):
        config.load_settings(env)


def test_short_signing_key_rejected_and_not_echoed():
    with pytest.raises(config.ConfigError, match="at least 32 bytes") as err:
        config.load_settings(parts_env(JWT_SIGNING_KEY="short-key-value"))
    assert "short-key-value" not in str(err.value)


def test_muse_model_and_base_url_defaults_and_overrides():
    settings = config.load_settings(parts_env())
    assert settings.muse_model == "muse-spark-1.3"
    assert settings.muse_base_url == "https://api.meta.ai/v1"
    settings = config.load_settings(parts_env(MUSE_MODEL="m2", MUSE_BASE_URL="https://example.test/v1"))
    assert (settings.muse_model, settings.muse_base_url) == ("m2", "https://example.test/v1")


def test_optional_keys_and_flags():
    settings = config.load_settings(parts_env())
    assert settings.deepinfra_api_key is None
    assert settings.langfuse_enabled is False
    assert settings.enable_docs is False
    settings = config.load_settings(
        parts_env(
            DEEPINFRA_API_KEY="di-test",
            LANGFUSE_PUBLIC_KEY="pk",
            LANGFUSE_SECRET_KEY="sk",
            AI_AGENT_ENABLE_DOCS="true",
            AI_AGENT_RATE_LIMIT_PER_MINUTE="5",
        )
    )
    assert settings.deepinfra_api_key == "di-test"
    assert settings.langfuse_enabled and settings.enable_docs
    assert settings.rate_limit_per_minute == 5


def test_invalid_flag_and_number():
    with pytest.raises(config.ConfigError) as err:
        config.load_settings(parts_env(AI_AGENT_ENABLE_DOCS="maybe", AI_AGENT_RATE_LIMIT_PER_MINUTE="x"))
    assert "AI_AGENT_ENABLE_DOCS" in str(err.value)
    assert "AI_AGENT_RATE_LIMIT_PER_MINUTE" in str(err.value)


def test_settings_repr_hides_secrets():
    text = repr(config.load_settings(parts_env(DEEPINFRA_API_KEY="di-secret")))
    for secret in (GOOD_KEY, "muse-test", "di-secret", "StudyTrackerDB"):
        assert secret not in text
