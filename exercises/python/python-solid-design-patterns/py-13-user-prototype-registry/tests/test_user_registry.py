import pytest

from user.cloneable import Cloneable
from user.user import User, UserType
from user.registry import UserPrototypeRegistry
from user.registry_impl import UserPrototypeRegistryImpl


@pytest.fixture
def registry():
    reg = UserPrototypeRegistryImpl()
    reg.add_prototype(User(1, 'alice', 'alice@example.com', 'Alice', 30, UserType.BASIC))
    reg.add_prototype(User(1, 'alice', 'alice@example.com', 'Alice', 30, UserType.PREMIUM))
    return reg


def test_clone_object_returns_an_equal_but_distinct_object():
    original = User(1, 'alice', 'alice@example.com', 'Alice', 30, UserType.BASIC)
    clone = original.clone_object()
    assert isinstance(clone, User), "clone_object must return a User"
    assert clone == original, "a clone has the same field values"
    assert clone is not original, "a clone must be a separate object"


def test_changing_a_clone_object_does_not_change_the_original():
    proto = User(1, 'alice', 'alice@example.com', 'Alice', 30, UserType.BASIC)
    clone = proto.clone_object()
    clone.username = 'mallory'
    clone.age = 99
    assert proto.username == 'alice' and proto.age == 30, "mutating the clone must not touch the original"


def test_registry_and_model_follow_the_prototype_interfaces():
    assert issubclass(User, Cloneable), "User must implement Cloneable"
    assert isinstance(UserPrototypeRegistryImpl(), UserPrototypeRegistry)


def test_get_prototype_returns_the_stored_prototype(registry):
    proto = registry.get_prototype(UserType.BASIC)
    assert proto == User(1, 'alice', 'alice@example.com', 'Alice', 30, UserType.BASIC)
    assert registry.get_prototype(UserType.BASIC) is proto, "get_prototype returns the stored object, not a copy"
    assert registry.get_prototype(UserType.PREMIUM) == User(1, 'alice', 'alice@example.com', 'Alice', 30, UserType.PREMIUM), "prototypes are keyed by type_"


def test_get_prototype_unknown_type_returns_none():
    assert UserPrototypeRegistryImpl().get_prototype(UserType.BASIC) is None


def test_clone_returns_a_copy_not_the_shared_prototype(registry):
    proto = registry.get_prototype(UserType.BASIC)
    first_clone = registry.clone(UserType.BASIC)
    second_clone = registry.clone(UserType.BASIC)
    assert first_clone == proto
    assert first_clone is not proto, "clone() must never hand out the stored prototype"
    assert first_clone is not second_clone, "every clone() call returns a new object"


def test_changing_a_registry_clone_does_not_change_the_stored_prototype(registry):
    clone = registry.clone(UserType.BASIC)
    clone.username = 'mallory'
    clone.age = 99
    proto = registry.get_prototype(UserType.BASIC)
    assert proto.username == 'alice' and proto.age == 30, "the stored prototype must be unaffected by changes to a clone"
    assert registry.clone(UserType.BASIC) == User(1, 'alice', 'alice@example.com', 'Alice', 30, UserType.BASIC), "later clones still start from the pristine prototype"


def test_clone_unknown_type_returns_none():
    reg = UserPrototypeRegistryImpl()
    reg.add_prototype(User(1, 'alice', 'alice@example.com', 'Alice', 30, UserType.BASIC))
    assert reg.clone(UserType.ADMIN) is None, "unknown type should give None"


def test_adding_a_prototype_of_an_existing_type_replaces_it():
    reg = UserPrototypeRegistryImpl()
    reg.add_prototype(User(1, 'alice', 'alice@example.com', 'Alice', 30, UserType.BASIC))
    replacement = User(1, 'alice', 'alice@example.com', 'Alice', 30, UserType.BASIC)
    replacement.username = "replaced"
    reg.add_prototype(replacement)
    assert reg.get_prototype(UserType.BASIC) is replacement, "one prototype per type: the newest wins"
