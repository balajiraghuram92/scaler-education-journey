from abc import ABC, abstractmethod

from .decoder import AudioDecoder, FLACDecoder, MP3Decoder
from .model import MediaFormat
from .player import AudioPlayer, FLACPlayer, MP3Player
from .processor import AudioProcessor, FLACAudioProcessor, MP3AudioProcessor


class AudioFactory(ABC):
    @abstractmethod
    def supports_format(self) -> MediaFormat:
        pass

    @abstractmethod
    def create_audio_player(self, volume: int, playback_rate: float) -> AudioPlayer:
        pass

    @abstractmethod
    def create_audio_decoder(self, audio_data: bytes) -> AudioDecoder:
        pass

    @abstractmethod
    def create_audio_processor(self, audio_data: bytes) -> AudioProcessor:
        pass


class FLACAudioFactory(AudioFactory):
    def supports_format(self) -> MediaFormat:
        return MediaFormat.FLAC

    def create_audio_player(self, volume: int, playback_rate: float) -> AudioPlayer:
        return FLACPlayer(volume, playback_rate)

    def create_audio_decoder(self, audio_data: bytes) -> AudioDecoder:
        return FLACDecoder(audio_data)

    def create_audio_processor(self, audio_data: bytes) -> AudioProcessor:
        return FLACAudioProcessor(audio_data)


class MP3AudioFactory(AudioFactory):
    def supports_format(self) -> MediaFormat:
        return MediaFormat.MP3

    def create_audio_player(self, volume: int, playback_rate: float) -> AudioPlayer:
        return MP3Player(volume, playback_rate)

    def create_audio_decoder(self, audio_data: bytes) -> AudioDecoder:
        return MP3Decoder(audio_data)

    def create_audio_processor(self, audio_data: bytes) -> AudioProcessor:
        return MP3AudioProcessor(audio_data)
