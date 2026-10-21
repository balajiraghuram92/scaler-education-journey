from config.db_config import DatabaseConfiguration

SETTERS = {
    "with_database_url": ("database_url", "jdbc:postgresql://localhost:5432/mydb"),
    "with_username": ("username", "user"),
    "with_password": ("password", "secret"),
    "with_max_connections": ("max_connections", 20),
    "with_enable_cache": ("enable_cache", True),
    "with_is_read_only": ("is_read_only", False),
}


def test_builder_returns_a_new_builder_each_time():
    assert DatabaseConfiguration.builder() is not DatabaseConfiguration.builder(), "builder() must create a fresh builder"


def test_every_setter_returns_the_same_builder_for_chaining():
    builder = DatabaseConfiguration.builder()
    for name, (_, value) in SETTERS.items():
        assert getattr(builder, name)(value) is builder, f"{name} must return the builder"


def test_every_setter_stores_its_value():
    for name, (field, value) in SETTERS.items():
        config = getattr(DatabaseConfiguration.builder(), name)(value).build()
        assert getattr(config, field) == value, f"{name} should set {field}"


def test_build_with_nothing_set_gives_all_none():
    config = DatabaseConfiguration.builder().build()
    assert isinstance(config, DatabaseConfiguration)
    assert config == DatabaseConfiguration(None, None, None, None, None, None)


def test_partial_configuration_leaves_other_fields_none():
    config = (
        DatabaseConfiguration.builder()
        .with_database_url("jdbc:postgresql://localhost/db")
        .with_username("user")
        .with_password("password")
        .build()
    )
    assert config.username == "user"
    assert config.max_connections is None and config.enable_cache is None and config.is_read_only is None


def test_full_chain_builds_the_expected_configuration():
    config = (
        DatabaseConfiguration.builder()
        .with_database_url("url")
        .with_username("u")
        .with_password("p")
        .with_max_connections(5)
        .with_enable_cache(False)
        .with_is_read_only(True)
        .build()
    )
    assert config == DatabaseConfiguration("url", "u", "p", 5, False, True)


def test_last_value_wins_when_a_setter_is_called_twice():
    config = DatabaseConfiguration.builder().with_username("a").with_username("b").build()
    assert config.username == "b"


def test_two_builders_do_not_share_state():
    first = DatabaseConfiguration.builder().with_username("first")
    second = DatabaseConfiguration.builder().with_username("second")
    assert first.build().username == "first" and second.build().username == "second"


def test_built_object_is_independent_of_the_builder():
    builder = DatabaseConfiguration.builder().with_username("alice").with_max_connections(5)
    first = builder.build()
    builder.with_username("bob")
    second = builder.build()
    assert first.username == "alice", "a reused builder must not change an object that was already built"
    assert second.username == "bob" and second.max_connections == 5
    assert first is not second, "each build() should return a new object"
