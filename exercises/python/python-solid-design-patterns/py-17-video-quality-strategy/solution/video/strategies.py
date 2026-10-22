from abc import ABC, abstractmethod

from .model import Video


class QualityAdjustmentStrategy(ABC):
    @abstractmethod
    def adjust_quality(self, video: Video) -> Video:
        pass


class LowQualityStrategy(QualityAdjustmentStrategy):
    def adjust_quality(self, video: Video) -> Video:
        video.quality = "Low"
        video.codec = "H264"
        video.bitrate = 500
        return video


class MediumQualityStrategy(QualityAdjustmentStrategy):
    def adjust_quality(self, video: Video) -> Video:
        video.quality = "Medium"
        video.codec = "H265"
        video.bitrate = 1000
        return video


class HighQualityStrategy(QualityAdjustmentStrategy):
    def adjust_quality(self, video: Video) -> Video:
        video.quality = "High"
        video.codec = "VP9"
        video.bitrate = 2000
        return video
