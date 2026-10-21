import inspect

import pytest

from declarative import Field, Model


class Ticket(Model):
    id = Field("INTEGER PRIMARY KEY")
    title = Field("TEXT")
    status = Field("TEXT", default="open")


class Bug(Ticket, table="defects"):
    severity = Field("INTEGER", default=3)


def test_fields_are_collected_in_declaration_order_with_inheritance() -> None:
    assert list(Ticket.__fields__) == ["id", "title", "status"]
    assert list(Bug.__fields__) == ["id", "title", "status", "severity"]
    assert "severity" not in Ticket.__fields__


def test_table_names_and_keyword_forwarding() -> None:
    assert Ticket.__table__ == "tickets"
    assert Bug.__table__ == "defects"


def test_create_sql() -> None:
    assert Ticket.create_sql() == (
        "CREATE TABLE tickets (id INTEGER PRIMARY KEY, title TEXT, status TEXT)"
    )
    assert Bug.create_sql().startswith("CREATE TABLE defects (")


def test_generated_signature_and_defaults() -> None:
    sig = inspect.signature(Bug)
    assert list(sig.parameters) == ["id", "title", "status", "severity"]
    t = Bug(id=1, title="boom")
    assert (t.id, t.title, t.status, t.severity) == (1, "boom", "open", 3)


def test_missing_and_unknown_arguments_raise_type_error() -> None:
    with pytest.raises(TypeError):
        Ticket(id=1)  # title is required
    with pytest.raises(TypeError):
        Ticket(id=1, title="x", colour="red")


def test_duplicate_definitions_fail_at_class_creation() -> None:
    with pytest.raises(TypeError, match="duplicate definition of 'title'"):
        class Bad(Model):
            title = Field("TEXT")
            title = Field("VARCHAR(10)")


def test_class_access_returns_field() -> None:
    assert isinstance(Ticket.title, Field)
    assert Ticket.title.name == "title"


def test_subclass_can_override_an_inherited_field_keeping_its_position() -> None:
    class Urgent(Ticket):
        status = Field("TEXT", default="triage")

    assert list(Urgent.__fields__) == ["id", "title", "status"], "override must not duplicate or reorder"
    assert Urgent.__fields__["status"].default == "triage"
    assert Ticket.__fields__["status"].default == "open", "the base class must keep its own field"
    assert Urgent(id=1, title="t").status == "triage"


def test_other_class_keywords_are_forwarded_to_type_new() -> None:
    seen: list[object] = []

    class Hooked(Model):
        def __init_subclass__(cls, flag: object = None, **kwargs: object) -> None:
            super().__init_subclass__(**kwargs)
            seen.append(flag)

    class Child(Hooked, flag="x", table="kids"):
        name = Field("TEXT")

    assert seen == ["x"], "unknown class keywords must reach __init_subclass__"
    assert Child.__table__ == "kids"


def test_instances_keep_their_own_values_in_the_instance_dict() -> None:
    a = Ticket(id=1, title="first")
    b = Ticket(id=2, title="second", status="closed")
    assert a.__dict__ == {"id": 1, "title": "first", "status": "open"}
    assert b.__dict__ == {"id": 2, "title": "second", "status": "closed"}
