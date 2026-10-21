from .processor import ImageProcessor
from .services import *


class ImageEditingManager:
    def __init__(
        self,
        image_loader: ImageLoader,
        filter_service: FilterService,
        image_modifier: ImageModifier,
        image_writer: ImageWriter,
        analytics_service: AnalyticsService,
    ):
        self.processor = ImageProcessor(
            image_loader,
            filter_service,
            image_modifier,
            image_writer,
            analytics_service,
        )

    def edit_image(self, image_path: str, filter_type: str, brightness: int) -> None:
        self.processor.process(image_path, filter_type, brightness)
