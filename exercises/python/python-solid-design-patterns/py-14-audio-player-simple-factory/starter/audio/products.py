from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class MediaFormat(Enum):
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"


@dataclass
class AudioPlayer(ABC):
    """Abstract product. Attributes: ``volume`` and ``playBackRate``."""

    volume: int
    playBackRate: float

    @abstractmethod
    def play(self):
        pass

    @abstractmethod
    def pause(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def supports_type(self):
        pass

    def set_volume(self, volume: int):
        """Shared behaviour: accept 0..100 (store it and print ``Volume set to <v>``);
        otherwise leave the volume unchanged and print ``Invalid volume level``."""
        raise NotImplementedError("Implement set_volume")


@dataclass
class MP3Player(AudioPlayer):
    """play() prints ``Playing MP3 audio``; pause()/stop() print their own line;
    supports_type() returns MediaFormat.MP3."""

    def play(self):
        raise NotImplementedError("Implement MP3Player.play")

    def pause(self):
        raise NotImplementedError("Implement MP3Player.pause")

    def stop(self):
        raise NotImplementedError("Implement MP3Player.stop")

    def supports_type(self):
        raise NotImplementedError("Implement MP3Player.supports_type")


@dataclass
class WAVPlayer(AudioPlayer):
    """play() prints ``Playing WAV audio``; supports_type() returns MediaFormat.WAV."""

    def play(self):
        raise NotImplementedError("Implement WAVPlayer.play")

    def pause(self):
        raise NotImplementedError("Implement WAVPlayer.pause")

    def stop(self):
        raise NotImplementedError("Implement WAVPlayer.stop")

    def supports_type(self):
        raise NotImplementedError("Implement WAVPlayer.supports_type")


@dataclass
class FLACPlayer(AudioPlayer):
    """play() prints ``Playing FLAC audio``; supports_type() returns MediaFormat.FLAC."""

    def play(self):
        raise NotImplementedError("Implement FLACPlayer.play")

    def pause(self):
        raise NotImplementedError("Implement FLACPlayer.pause")

    def stop(self):
        raise NotImplementedError("Implement FLACPlayer.stop")

    def supports_type(self):
        raise NotImplementedError("Implement FLACPlayer.supports_type")
