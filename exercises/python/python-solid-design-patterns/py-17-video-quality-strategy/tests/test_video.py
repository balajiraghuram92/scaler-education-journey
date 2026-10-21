import inspect
from types import SimpleNamespace

import pytest

from video.manager import VideoStreamingManager
from video.model import Video, VideoQuality
from video.strategies import (
    HighQualityStrategy,
    LowQualityStrategy,
    MediumQualityStrategy,
    QualityAdjustmentStrategy,
)

TABLE = [
    (LowQualityStrategy, "Low", "H264", 500),
    (MediumQualityStrategy, "Medium", "H265", 1000),
    (HighQualityStrategy, "High", "VP9", 2000),
]


def test_interface_is_abstract_and_declares_adjust_quality():
    assert inspect.isabstract(QualityAdjustmentStrategy), "QualityAdjustmentStrategy must be an ABC with an abstract method"
    assert "adjust_quality" in QualityAdjustmentStrategy.__abstractmethods__
    with pytest.raises(TypeError):
        QualityAdjustmentStrategy()
    for cls, *_ in TABLE:
        assert issubclass(cls, QualityAdjustmentStrategy) and not inspect.isabstract(cls), (
            f"{cls.__name__} must be a concrete QualityAdjustmentStrategy"
        )


def test_low_quality_settings():
    video = SimpleNamespace(quality="High")
    LowQualityStrategy().adjust_quality(video)
    assert (video.quality, video.codec, video.bitrate) == ("Low", "H264", 500)


def test_medium_quality_settings():
    video = SimpleNamespace(quality="Low")
    MediumQualityStrategy().adjust_quality(video)
    assert (video.quality, video.codec, video.bitrate) == ("Medium", "H265", 1000)


def test_high_quality_settings():
    video = SimpleNamespace(quality="Medium")
    HighQualityStrategy().adjust_quality(video)
    assert (video.quality, video.codec, video.bitrate) == ("High", "VP9", 2000)


def test_strategies_return_the_same_video_object():
    for cls, *_ in TABLE:
        video = Video(VideoQuality.LOW)
        assert cls().adjust_quality(video) is video, f"{cls.__name__} must mutate and return the same Video, not a copy"


def test_strategies_leave_other_attributes_alone():
    video = SimpleNamespace(quality="x", title="Holiday", duration=90)
    HighQualityStrategy().adjust_quality(video)
    assert (video.title, video.duration) == ("Holiday", 90), "only quality, codec and bitrate may change"


def test_manager_applies_its_strategy_and_returns_the_video():
    video = Video(VideoQuality.MEDIUM)
    result = VideoStreamingManager(video, LowQualityStrategy()).stream_video()
    assert result is video
    assert (video.quality, video.codec, video.bitrate) == ("Low", "H264", 500)


def test_strategy_can_be_swapped_at_runtime():
    video = Video(VideoQuality.LOW)
    manager = VideoStreamingManager(video, LowQualityStrategy())
    manager.stream_video()
    manager.adjustment_strategy = HighQualityStrategy()
    manager.stream_video()
    assert (video.quality, video.codec, video.bitrate) == ("High", "VP9", 2000), "the new strategy must override the old settings"
    manager.adjustment_strategy = MediumQualityStrategy()
    manager.stream_video()
    assert (video.quality, video.codec, video.bitrate) == ("Medium", "H265", 1000)


def test_custom_strategy_works_without_touching_the_manager():
    class Adaptive(QualityAdjustmentStrategy):
        def adjust_quality(self, video):
            video.quality, video.codec, video.bitrate = "Auto", "AV1", 1500
            return video

    video = Video(VideoQuality.LOW)
    assert VideoStreamingManager(video, Adaptive()).stream_video().bitrate == 1500
