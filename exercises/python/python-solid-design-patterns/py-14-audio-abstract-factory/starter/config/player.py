from abc import ABC, abstractmethod
from dataclasses import dataclass

from .model import MediaFormat


@dataclass
class AudioPlayer(ABC):
    volume: int
    playback_rate: float

    @abstractmethod
    def supports_format(self) -> MediaFormat:
        pass


@dataclass
class MP3Player(AudioPlayer):
    def supports_format(self) -> MediaFormat:
        return MediaFormat.MP3


@dataclass
class FLACPlayer(AudioPlayer):
    def supports_format(self) -> MediaFormat:
        return MediaFormat.FLAC
