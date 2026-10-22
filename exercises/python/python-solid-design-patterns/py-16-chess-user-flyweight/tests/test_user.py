from dataclasses import fields, is_dataclass

from config.model import ChessUser, Colour, UserExtrinsicState, UserIntrinsicState
from config.registry import FlyweightRegistry, FlyweightRegistryImpl


def make_user(email="ada@example.com", photo=None):
    return UserIntrinsicState(
        "Ada", 36, "female", email, "555-0100", photo if photo is not None else b"\x89PNG" + b"0" * 1024
    )


def names(cls):
    return {f.name for f in fields(cls)}


def test_intrinsic_state_has_the_shared_fields():
    assert is_dataclass(UserIntrinsicState), "UserIntrinsicState must be a dataclass"
    assert names(UserIntrinsicState) == {"name", "age", "gender", "email", "phone_number", "photo"}, (
        f"intrinsic state fields are wrong: {sorted(names(UserIntrinsicState))}"
    )


def test_extrinsic_state_has_per_game_fields_and_a_reference():
    assert is_dataclass(UserExtrinsicState), "UserExtrinsicState must be a dataclass"
    assert names(UserExtrinsicState) == {"colour", "current_game_streak", "intrinsic_state"}, (
        f"extrinsic state fields are wrong: {sorted(names(UserExtrinsicState))}"
    )


def test_original_chess_user_is_untouched():
    assert [f.name for f in fields(ChessUser)] == [
        "name", "age", "gender", "email", "phone_number", "colour", "current_game_streak", "photo",
    ], "ChessUser must keep its original fields"


def test_registry_returns_the_very_same_object_it_was_given():
    registry = FlyweightRegistryImpl()
    fw = make_user()
    registry.add_flyweight(fw)
    assert registry.get_flyweight("ada@example.com") is fw, "return the stored flyweight itself, not a copy"
    assert isinstance(registry, FlyweightRegistry)


def test_missing_email_returns_none():
    registry = FlyweightRegistryImpl()
    assert registry.get_flyweight("nobody@example.com") is None, "empty registry must return None"
    registry.add_flyweight(make_user())
    assert registry.get_flyweight("other@example.com") is None, "unknown email must return None"


def test_storage_is_a_dict_keyed_by_email():
    registry = FlyweightRegistryImpl()
    a, b = make_user("a@x.com"), make_user("b@x.com")
    registry.add_flyweight(a)
    registry.add_flyweight(b)
    assert isinstance(registry._flyweights, dict), "storage must be a dict named _flyweights"
    assert set(registry._flyweights) == {"a@x.com", "b@x.com"}
    assert registry._flyweights["b@x.com"] is b


def test_adding_the_same_email_again_replaces_the_entry():
    registry = FlyweightRegistryImpl()
    old, new = make_user(), make_user()
    registry.add_flyweight(old)
    registry.add_flyweight(new)
    assert len(registry._flyweights) == 1, "one entry per email"
    assert registry.get_flyweight("ada@example.com") is new


def test_registries_do_not_share_storage():
    r1, r2 = FlyweightRegistryImpl(), FlyweightRegistryImpl()
    r1.add_flyweight(make_user())
    assert r2.get_flyweight("ada@example.com") is None, "storage must be per instance, not a class-level dict"


def test_many_games_share_one_intrinsic_state():
    registry = FlyweightRegistryImpl()
    registry.add_flyweight(make_user())
    games = [
        UserExtrinsicState(Colour.WHITE if i % 2 else Colour.BLACK, i, registry.get_flyweight("ada@example.com"))
        for i in range(500)
    ]
    first = games[0].intrinsic_state
    assert all(g.intrinsic_state is first for g in games), "all games must point at the same shared flyweight"
    assert len({id(g.intrinsic_state.photo) for g in games}) == 1, "the large photo must exist once, not once per game"
    assert games[3].current_game_streak == 3 and games[3].colour is Colour.WHITE, "extrinsic state stays per game"
