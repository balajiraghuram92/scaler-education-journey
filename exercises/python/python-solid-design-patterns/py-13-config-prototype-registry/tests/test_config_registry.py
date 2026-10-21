import pytest

from config.cloneable import Cloneable
from config.app_config import Configuration, ConfigurationType
from config.registry import ConfigurationPrototypeRegistry
from config.registry_impl import ConfigurationPrototypeRegistryImpl


@pytest.fixture
def registry():
    reg = ConfigurationPrototypeRegistryImpl()
    reg.add_prototype(Configuration('blue', True, 'en', False, 12, 'Arial', ConfigurationType.BASIC))
    reg.add_prototype(Configuration('blue', True, 'en', False, 12, 'Arial', ConfigurationType.ADVANCED))
    return reg


def test_clone_object_returns_an_equal_but_distinct_object():
    original = Configuration('blue', True, 'en', False, 12, 'Arial', ConfigurationType.BASIC)
    clone = original.clone_object()
    assert isinstance(clone, Configuration), "clone_object must return a Configuration"
    assert clone == original, "a clone has the same field values"
    assert clone is not original, "a clone must be a separate object"


def test_changing_a_clone_object_does_not_change_the_original():
    proto = Configuration('blue', True, 'en', False, 12, 'Arial', ConfigurationType.BASIC)
    clone = proto.clone_object()
    clone.theme_color = 'red'
    clone.font_size = 40
    assert proto.theme_color == 'blue' and proto.font_size == 12, "mutating the clone must not touch the original"


def test_registry_and_model_follow_the_prototype_interfaces():
    assert issubclass(Configuration, Cloneable), "Configuration must implement Cloneable"
    assert isinstance(ConfigurationPrototypeRegistryImpl(), ConfigurationPrototypeRegistry)


def test_get_prototype_returns_the_stored_prototype(registry):
    proto = registry.get_prototype(ConfigurationType.BASIC)
    assert proto == Configuration('blue', True, 'en', False, 12, 'Arial', ConfigurationType.BASIC)
    assert registry.get_prototype(ConfigurationType.BASIC) is proto, "get_prototype returns the stored object, not a copy"
    assert registry.get_prototype(ConfigurationType.ADVANCED) == Configuration('blue', True, 'en', False, 12, 'Arial', ConfigurationType.ADVANCED), "prototypes are keyed by type_"


def test_get_prototype_unknown_type_returns_none():
    assert ConfigurationPrototypeRegistryImpl().get_prototype(ConfigurationType.BASIC) is None


def test_clone_returns_a_copy_not_the_shared_prototype(registry):
    proto = registry.get_prototype(ConfigurationType.BASIC)
    first_clone = registry.clone(ConfigurationType.BASIC)
    second_clone = registry.clone(ConfigurationType.BASIC)
    assert first_clone == proto
    assert first_clone is not proto, "clone() must never hand out the stored prototype"
    assert first_clone is not second_clone, "every clone() call returns a new object"


def test_changing_a_registry_clone_does_not_change_the_stored_prototype(registry):
    clone = registry.clone(ConfigurationType.BASIC)
    clone.theme_color = 'red'
    clone.font_size = 40
    proto = registry.get_prototype(ConfigurationType.BASIC)
    assert proto.theme_color == 'blue' and proto.font_size == 12, "the stored prototype must be unaffected by changes to a clone"
    assert registry.clone(ConfigurationType.BASIC) == Configuration('blue', True, 'en', False, 12, 'Arial', ConfigurationType.BASIC), "later clones still start from the pristine prototype"


def test_clone_unknown_type_returns_none():
    reg = ConfigurationPrototypeRegistryImpl()
    reg.add_prototype(Configuration('blue', True, 'en', False, 12, 'Arial', ConfigurationType.BASIC))
    assert reg.clone(ConfigurationType.DEFAULT) is None, "unknown type should give None"


def test_adding_a_prototype_of_an_existing_type_replaces_it():
    reg = ConfigurationPrototypeRegistryImpl()
    reg.add_prototype(Configuration('blue', True, 'en', False, 12, 'Arial', ConfigurationType.BASIC))
    replacement = Configuration('blue', True, 'en', False, 12, 'Arial', ConfigurationType.BASIC)
    replacement.theme_color = "replaced"
    reg.add_prototype(replacement)
    assert reg.get_prototype(ConfigurationType.BASIC) is replacement, "one prototype per type: the newest wins"
