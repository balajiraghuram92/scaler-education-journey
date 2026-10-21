from abc import ABC, abstractmethod
from dataclasses import dataclass

from .model import MediaFormat


@dataclass
class AudioProcessor(ABC):
    audio_data: bytes

    @abstractmethod
    def supports_format(self) -> MediaFormat:
        pass


@dataclass
class MP3AudioProcessor(AudioProcessor):
    def supports_format(self) -> MediaFormat:
        return MediaFormat.MP3


@dataclass
class FLACAudioProcessor(AudioProcessor):
    def supports_format(self) -> MediaFormat:
        return MediaFormat.FLAC
