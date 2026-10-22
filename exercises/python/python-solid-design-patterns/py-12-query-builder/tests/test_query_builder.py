from config.query_builder import Query

CLAUSES = {
    "select": "SELECT name, age",
    "from_": "FROM users",
    "where": "WHERE age > 18",
    "join": "JOIN orders ON orders.user_id = users.id",
    "order_by": "ORDER BY age",
    "group_by": "GROUP BY age",
}


def test_builder_returns_a_new_builder_each_time():
    assert Query.builder() is not Query.builder(), "builder() must create a fresh builder"


def test_every_setter_returns_the_same_builder_for_chaining():
    builder = Query.builder()
    for name, value in CLAUSES.items():
        assert getattr(builder, name)(value) is builder, f"{name} must return the builder"


def test_every_setter_stores_its_clause():
    for name, value in CLAUSES.items():
        query = getattr(Query.builder(), name)(value).build()
        assert getattr(query, name) == value, f"{name} should set the {name} field"


def test_build_with_nothing_set_gives_all_none():
    query = Query.builder().build()
    assert isinstance(query, Query)
    assert query == Query(None, None, None, None, None, None)


def test_partial_query_leaves_other_clauses_none():
    query = Query.builder().select("SELECT name, age").from_("FROM users").where("WHERE age > 18").build()
    assert query.where == "WHERE age > 18"
    assert query.join is None and query.order_by is None and query.group_by is None


def test_full_chain_builds_the_expected_query():
    query = (
        Query.builder()
        .select("s").from_("f").where("w").join("j").order_by("o").group_by("g")
        .build()
    )
    assert query == Query("s", "f", "w", "j", "o", "g")


def test_two_builders_do_not_share_state():
    first = Query.builder().select("SELECT a")
    second = Query.builder().select("SELECT b")
    assert first.build().select == "SELECT a" and second.build().select == "SELECT b"


def test_built_object_is_independent_of_the_builder():
    builder = Query.builder().select("SELECT a").from_("FROM t")
    first = builder.build()
    builder.select("SELECT b")
    second = builder.build()
    assert first.select == "SELECT a", "a reused builder must not change an object that was already built"
    assert second.select == "SELECT b" and second.from_ == "FROM t"
    assert first is not second, "each build() should return a new object"
