from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


@dataclass
class AudioPlayer(ABC):
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
        if 0 <= volume <= 100:
            self.volume = volume
            print("Volume set to", volume)
        else:
            print("Invalid volume level")


class MediaFormat(Enum):
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"


@dataclass
class FLACPlayer(AudioPlayer):

    def play(self):
        print("Playing FLAC audio")

    def pause(self):
        print("Pausing FLAC audio")

    def stop(self):
        print("Stopping FLAC audio")

    def supports_type(self):
        return MediaFormat.FLAC


@dataclass
class MP3Player(AudioPlayer):

    def play(self):
        print("Playing MP3 audio")

    def pause(self):
        print("Pausing MP3 audio")

    def stop(self):
        print("Stopping MP3 audio")

    def supports_type(self):
        return MediaFormat.MP3


@dataclass
class WAVPlayer(AudioPlayer):

    def play(self):
        print("Playing WAV audio")

    def pause(self):
        print("Pausing WAV audio")

    def stop(self):
        print("Stopping WAV audio")

    def supports_type(self):
        return MediaFormat.WAV
