from .services import (
    ImageLoader,
    FilterService,
    ImageModifier,
    ImageWriter,
    AnalyticsService,
)
from .model import Image


class ImageProcessor:
    """Facade over the five image services.

    __init__ takes image_loader, filter_service, image_modifier, image_writer and
    analytics_service, in that order (the same as ImageEditingManager.__init__).
    """

    def __init__(
        self,
        image_loader: ImageLoader,
        filter_service: FilterService,
        image_modifier: ImageModifier,
        image_writer: ImageWriter,
        analytics_service: AnalyticsService,
    ):
        raise NotImplementedError("Store the five services")

    def process(self, image_path: str, filter_type: str, brightness: int) -> None:
        """Run, in order: load_image(image_path), apply_filter(image, filter_type),
        adjust_brightness(image, brightness), save_image(image), store(image).

        The image returned by load_image is the one passed to every later step.
        """
        raise NotImplementedError("Implement the editing workflow")
