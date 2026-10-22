from .services import (
    ImageLoader,
    FilterService,
    ImageModifier,
    ImageWriter,
    AnalyticsService,
)
from .model import Image


class ImageProcessor:
    def __init__(
        self,
        image_loader: ImageLoader,
        filter_service: FilterService,
        image_modifier: ImageModifier,
        image_writer: ImageWriter,
        analytics_service: AnalyticsService,
    ):
        self.image_loader = image_loader
        self.filter_service = filter_service
        self.image_modifier = image_modifier
        self.image_writer = image_writer
        self.analytics_service = analytics_service

    def process(self, image_path: str, filter_type: str, brightness: int) -> None:
        image: Image = self.image_loader.load_image(image_path)

        self.filter_service.apply_filter(image, filter_type)
        self.image_modifier.adjust_brightness(image, brightness)

        self.image_writer.save_image(image)
        self.analytics_service.store(image)
