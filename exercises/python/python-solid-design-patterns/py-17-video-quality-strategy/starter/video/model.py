from dataclasses import dataclass
from enum import Enum


class VideoQuality(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class VideoCodec(Enum):
    H264 = "H264"
    H265 = "H265"
    VP9 = "VP9"


@dataclass
class Video:
    quality: VideoQuality
    codec: VideoCodec = None
    bitrate: int = None
