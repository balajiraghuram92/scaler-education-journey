from abc import ABC, abstractmethod

from .model import Video


class QualityAdjustmentStrategy(ABC):
    """Strategy interface.

    Declare one abstract method: adjust_quality(self, video: Video) -> Video
    """


class LowQualityStrategy(QualityAdjustmentStrategy):
    """Set video.quality = "Low", video.codec = "H264", video.bitrate = 500; return the same video."""


class MediumQualityStrategy(QualityAdjustmentStrategy):
    """Set video.quality = "Medium", video.codec = "H265", video.bitrate = 1000; return the same video."""


class HighQualityStrategy(QualityAdjustmentStrategy):
    """Set video.quality = "High", video.codec = "VP9", video.bitrate = 2000; return the same video."""
