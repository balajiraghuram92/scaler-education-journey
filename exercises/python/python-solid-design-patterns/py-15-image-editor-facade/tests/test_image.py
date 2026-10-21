import pytest

from image.manager import ImageEditingManager
from image.model import Image
from image.processor import ImageProcessor
from image.services import (
    AnalyticsService,
    FilterService,
    ImageLoader,
    ImageModifier,
    ImageWriter,
)


class Rig:
    def __init__(self, fail_at=None):
        self.log = []
        self.image = Image()
        rig = self

        class Loader:
            def load_image(self, path):
                rig.log.append(("load", path))
                if fail_at == "load":
                    raise FileNotFoundError(path)
                return rig.image

        class Filters:
            def apply_filter(self, image, filter_type):
                rig.log.append(("filter", image, filter_type))
                if fail_at == "filter":
                    raise ValueError(filter_type)

        class Modifier:
            def adjust_brightness(self, image, brightness):
                rig.log.append(("brightness", image, brightness))

        class Writer:
            def save_image(self, image):
                rig.log.append(("save", image))

        class Analytics:
            def store(self, image):
                rig.log.append(("store", image))

        self.services = (Loader(), Filters(), Modifier(), Writer(), Analytics())

    def names(self):
        return [e[0] for e in self.log]


def test_manager_does_not_expose_the_services():
    manager = ImageEditingManager(
        ImageLoader(), FilterService(), ImageModifier(), ImageWriter(), AnalyticsService()
    )
    for name in ("image_loader", "filter_service", "image_modifier", "image_writer", "analytics_service"):
        assert not hasattr(manager, name), f"ImageEditingManager must not expose {name}"


def test_workflow_runs_in_order():
    rig = Rig()
    ImageProcessor(*rig.services).process("/p.jpg", "sepia", 40)
    assert rig.names() == ["load", "filter", "brightness", "save", "store"], f"wrong order: {rig.names()}"


def test_same_image_object_flows_through_every_step():
    rig = Rig()
    ImageProcessor(*rig.services).process("/p.jpg", "sepia", 40)
    for entry in rig.log[1:]:
        assert entry[1] is rig.image, f"{entry[0]} must receive the image returned by load_image"


def test_arguments_reach_the_right_services():
    rig = Rig()
    ImageProcessor(*rig.services).process("/path/to/image.jpg", "sepia", 50)
    by_name = {e[0]: e for e in rig.log}
    assert by_name["load"] == ("load", "/path/to/image.jpg")
    assert by_name["filter"][2] == "sepia"
    assert by_name["brightness"][2] == 50


def test_process_returns_none_and_does_not_print(capsys):
    rig = Rig()
    assert ImageProcessor(*rig.services).process("/p.jpg", "blur", 0) is None
    assert capsys.readouterr().out == "", "the facade must not print"


def test_constructor_order_matches_the_manager():
    rig = Rig()
    ImageEditingManager(*rig.services).edit_image("/p.jpg", "mono", 10)
    assert rig.names() == ["load", "filter", "brightness", "save", "store"], (
        "services must be wired in the order loader, filter, modifier, writer, analytics"
    )


@pytest.mark.parametrize("fail_at,expected", [
    ("load", ["load"]),
    ("filter", ["load", "filter"]),
])
def test_failure_stops_later_steps(fail_at, expected):
    rig = Rig(fail_at=fail_at)
    with pytest.raises((FileNotFoundError, ValueError)):
        ImageProcessor(*rig.services).process("/p.jpg", "sepia", 1)
    assert rig.names() == expected, f"nothing after the failing step may run, ran {rig.names()}"


def test_works_with_the_default_services():
    manager = ImageEditingManager(
        ImageLoader(), FilterService(), ImageModifier(), ImageWriter(), AnalyticsService()
    )
    assert manager.edit_image("/x.png", "sepia", 5) is None
