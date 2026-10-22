from dataclasses import FrozenInstanceError

import pytest

from dbconfig import DatabaseConfiguration


def valid_builder():
    return (
        DatabaseConfiguration.builder()
        .with_database_url("postgresql://db.internal/app")
        .with_credentials("svc", "s3cret")
    )


def test_build_with_defaults():
    config = valid_builder().build()
    assert isinstance(config, DatabaseConfiguration)
    assert config.database_url == "postgresql://db.internal/app"
    assert (config.username, config.password) == ("svc", "s3cret")
    assert config.max_connections == 10, "default max_connections is 10"
    assert config.enable_cache is False and config.read_only is False
    assert config.allowed_hosts == ()


def test_setters_return_the_builder_and_are_applied():
    builder = valid_builder()
    assert builder.with_max_connections(50) is builder, "setters must return the builder"
    config = (
        builder.with_enable_cache(True)
        .with_read_only(True)
        .with_allowed_host("10.0.0.1")
        .with_allowed_host("10.0.0.2")
        .build()
    )
    assert (config.max_connections, config.enable_cache, config.read_only) == (50, True, True)
    assert config.allowed_hosts == ("10.0.0.1", "10.0.0.2"), "with_allowed_host appends in order"
    assert isinstance(config.allowed_hosts, tuple)


def test_all_problems_are_reported_together():
    with pytest.raises(ValueError) as info:
        DatabaseConfiguration.builder().with_max_connections(0).build()
    message = str(info.value)
    assert "database_url" in message and "credentials" in message and "max_connections" in message, (
        f"every problem must be listed in one error, got: {message!r}"
    )
    assert message.count("; ") >= 2, "problems are joined with '; '"


def test_url_scheme_is_validated():
    with pytest.raises(ValueError, match="postgresql://"):
        valid_builder().with_database_url("sqlite:///x.db").build()
    assert valid_builder().with_database_url("mysql://host/db").build().database_url == "mysql://host/db"


def test_credentials_are_required():
    with pytest.raises(ValueError, match="credentials"):
        DatabaseConfiguration.builder().with_database_url("postgresql://h/d").build()
    with pytest.raises(ValueError, match="credentials"):
        valid_builder().with_credentials("svc", "").build()


@pytest.mark.parametrize("bad", [0, 501, -3])
def test_max_connections_outside_range_is_rejected(bad):
    with pytest.raises(ValueError, match="max_connections"):
        valid_builder().with_max_connections(bad).build()
    assert valid_builder().with_max_connections(1).build().max_connections == 1
    assert valid_builder().with_max_connections(500).build().max_connections == 500


def test_each_build_returns_a_new_object():
    builder = valid_builder()
    first, second = builder.build(), builder.build()
    assert first is not second and first == second


def test_later_builder_changes_do_not_affect_built_objects():
    builder = valid_builder().with_allowed_host("10.0.0.1")
    first = builder.build()
    builder.with_allowed_host("10.0.0.2").with_max_connections(99)
    assert first.allowed_hosts == ("10.0.0.1",), "the built object must not see later hosts"
    assert first.max_connections == 10


def test_product_is_immutable_and_hides_the_password():
    config = valid_builder().build()
    with pytest.raises(FrozenInstanceError):
        config.max_connections = 5
    assert "s3cret" not in repr(config), "the password must not appear in repr"
    assert "svc" in repr(config)
