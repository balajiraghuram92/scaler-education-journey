import pytest

from database import Database
from database_factory import DatabaseFactory
from database_type import DatabaseType
from databases.mongodb_database import MongoDBDatabase
from databases.mysql_database import MySQLDatabase
from databases.postgresql_database import PostgreSQLDatabase

EXPECTED = {
    DatabaseType.MYSQL: MySQLDatabase,
    DatabaseType.POSTGRE_SQL: PostgreSQLDatabase,
    DatabaseType.MONGO_DB: MongoDBDatabase,
}


@pytest.mark.parametrize("db_type", list(DatabaseType))
def test_factory_creates_each_database(db_type):
    db = DatabaseFactory.create_database(db_type, "d")
    assert type(db) is EXPECTED[db_type], f"{db_type} should create {EXPECTED[db_type].__name__}"
    assert isinstance(db, Database)


@pytest.mark.parametrize("db_type", list(DatabaseType))
def test_created_database_supports_its_type(db_type):
    assert DatabaseFactory.create_database(db_type, "d").supports_type() is db_type


def test_name_is_stored_by_the_parent():
    db = DatabaseFactory.create_database(DatabaseType.MYSQL, "orders")
    assert db.get_database_name() == "orders"
    assert db.database_name == "orders"


@pytest.mark.parametrize("bad", [None, "MYSQL", 42, object()])
def test_unknown_type_raises_value_error(bad):
    with pytest.raises(ValueError):
        DatabaseFactory.create_database(bad, "x")


def test_database_is_abstract():
    with pytest.raises(TypeError):
        Database("x")
    assert {"database_connection", "supports_type"} <= set(Database.__abstractmethods__)


def test_incomplete_subclass_cannot_be_instantiated():
    class Half(Database):
        def database_connection(self):
            pass

    with pytest.raises(TypeError):
        Half("half")


def test_shared_behaviour_lives_in_the_parent():
    assert "get_database_name" not in Database.__abstractmethods__
    assert "get_database_name" in vars(Database)
    for cls in EXPECTED.values():
        assert "get_database_name" not in vars(cls), f"{cls.__name__} must inherit the accessor"
        assert "database_name" not in vars(cls)


@pytest.mark.parametrize("db_type", list(DatabaseType))
def test_each_database_connects(db_type, capsys):
    DatabaseFactory.create_database(db_type, "d").database_connection()
    assert capsys.readouterr().out.strip() != ""


def test_factory_returns_new_instances():
    a = DatabaseFactory.create_database(DatabaseType.MONGO_DB, "a")
    b = DatabaseFactory.create_database(DatabaseType.MONGO_DB, "b")
    assert a is not b
    assert (a.get_database_name(), b.get_database_name()) == ("a", "b")
