from dataclasses import dataclass

from .model import Video
from .strategies import QualityAdjustmentStrategy


@dataclass
class VideoStreamingManager:

    def __init__(self, video: Video, adjustment_strategy: QualityAdjustmentStrategy):
        self.video = video
        self.adjustment_strategy = adjustment_strategy

    def stream_video(self) -> Video:
        return self.adjustment_strategy.adjust_quality(self.video)
