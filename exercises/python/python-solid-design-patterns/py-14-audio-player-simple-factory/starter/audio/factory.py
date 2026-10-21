from .products import *


class AudioPlayerFactory:
    """Simple Factory: callers pass a MediaFormat and never name a concrete player."""

    @staticmethod
    def create_audio_player(type_: MediaFormat, volume: int, playBackRate: float) -> AudioPlayer:
        """Return the player for ``type_`` built with ``(volume, playBackRate)``.

        Construct ONLY the selected player. An unsupported ``type_`` raises
        ValueError (not an obscure TypeError).
        """
        raise NotImplementedError("Implement create_audio_player")
