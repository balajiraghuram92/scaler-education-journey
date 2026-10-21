from dataclasses import fields, is_dataclass

from config.model import (
    Graphic,
    GraphicExtrinsicState,
    GraphicIntrinsicState,
    GraphicType,
    Image,
)
from config.registry import FlyweightRegistry, FlyweightRegistryImpl


def make(type_=GraphicType.PNG, colour="red"):
    return GraphicIntrinsicState(image=Image(), width=100, height=50, colour=colour, type=type_)


def names(cls):
    return {f.name for f in fields(cls)}


def test_intrinsic_state_has_the_shared_fields():
    assert is_dataclass(GraphicIntrinsicState), "GraphicIntrinsicState must be a dataclass"
    assert names(GraphicIntrinsicState) == {"image", "width", "height", "colour", "type"}, (
        f"intrinsic fields are wrong: {sorted(names(GraphicIntrinsicState))}"
    )


def test_extrinsic_state_has_placement_fields_and_a_reference():
    assert is_dataclass(GraphicExtrinsicState), "GraphicExtrinsicState must be a dataclass"
    assert names(GraphicExtrinsicState) == {"x", "y", "intrinsic_state"}, (
        f"extrinsic fields are wrong: {sorted(names(GraphicExtrinsicState))}"
    )


def test_original_graphic_is_untouched():
    assert [f.name for f in fields(Graphic)] == ["type", "image", "x", "y", "width", "height", "colour"]


def test_registry_returns_the_very_same_object():
    registry = FlyweightRegistryImpl()
    fw = make(GraphicType.JPEG)
    registry.add_flyweight(fw)
    assert registry.get_flyweight(GraphicType.JPEG) is fw, "return the stored flyweight itself, not a copy"
    assert isinstance(registry, FlyweightRegistry)


def test_missing_type_returns_none():
    registry = FlyweightRegistryImpl()
    assert registry.get_flyweight(GraphicType.SVG) is None, "empty registry must return None"
    registry.add_flyweight(make(GraphicType.PNG))
    assert registry.get_flyweight(GraphicType.SVG) is None, "unknown type must return None"


def test_storage_is_a_dict_keyed_by_graphic_type():
    registry = FlyweightRegistryImpl()
    png, svg = make(GraphicType.PNG), make(GraphicType.SVG)
    registry.add_flyweight(png)
    registry.add_flyweight(svg)
    assert isinstance(registry._flyweights, dict), "storage must be a dict named _flyweights"
    assert set(registry._flyweights) == {GraphicType.PNG, GraphicType.SVG}
    assert registry._flyweights[GraphicType.SVG] is svg


def test_adding_the_same_type_again_replaces_the_entry():
    registry = FlyweightRegistryImpl()
    old, new = make(colour="red"), make(colour="blue")
    registry.add_flyweight(old)
    registry.add_flyweight(new)
    assert len(registry._flyweights) == 1, "one entry per graphic type"
    assert registry.get_flyweight(GraphicType.PNG) is new


def test_registries_do_not_share_storage():
    r1, r2 = FlyweightRegistryImpl(), FlyweightRegistryImpl()
    r1.add_flyweight(make())
    assert r2.get_flyweight(GraphicType.PNG) is None, "storage must be per instance, not a class-level dict"


def test_many_placements_share_one_intrinsic_state():
    registry = FlyweightRegistryImpl()
    registry.add_flyweight(make(GraphicType.PNG))
    placed = [GraphicExtrinsicState(i, i * 2, registry.get_flyweight(GraphicType.PNG)) for i in range(300)]
    shared = placed[0].intrinsic_state
    assert all(p.intrinsic_state is shared for p in placed), "every placement must reference the same flyweight"
    assert len({id(p.intrinsic_state.image) for p in placed}) == 1, "the image must exist once"
    assert (placed[7].x, placed[7].y) == (7, 14), "x and y stay per placement"
