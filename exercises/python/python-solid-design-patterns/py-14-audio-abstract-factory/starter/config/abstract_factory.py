from abc import ABC, abstractmethod

from .decoder import AudioDecoder, FLACDecoder, MP3Decoder
from .model import MediaFormat
from .player import AudioPlayer, FLACPlayer, MP3Player
from .processor import AudioProcessor, FLACAudioProcessor, MP3AudioProcessor


class AudioFactory(ABC):
    """Abstract Factory for one audio format family.

    Declare FOUR abstract methods (so AudioFactory cannot be instantiated):
      supports_format() -> MediaFormat
      create_audio_player(volume, playback_rate) -> AudioPlayer
      create_audio_decoder(audio_data) -> AudioDecoder
      create_audio_processor(audio_data) -> AudioProcessor
    """


class MP3AudioFactory(AudioFactory):
    """Implement all four methods; create only MP3 products."""


class FLACAudioFactory(AudioFactory):
    """Implement all four methods; create only FLAC products."""
