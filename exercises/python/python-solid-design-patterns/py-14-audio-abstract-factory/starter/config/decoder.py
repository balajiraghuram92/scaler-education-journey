from abc import ABC, abstractmethod
from dataclasses import dataclass

from .model import MediaFormat


@dataclass
class AudioDecoder(ABC):
    audio_data: bytes

    @abstractmethod
    def supports_format(self) -> MediaFormat:
        pass


@dataclass
class MP3Decoder(AudioDecoder):
    def supports_format(self) -> MediaFormat:
        return MediaFormat.MP3


@dataclass
class FLACDecoder(AudioDecoder):
    def supports_format(self) -> MediaFormat:
        return MediaFormat.FLAC
