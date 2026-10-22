from .products import *


class AudioPlayerFactory:
    _PLAYERS = {
        MediaFormat.MP3: MP3Player,
        MediaFormat.WAV: WAVPlayer,
        MediaFormat.FLAC: FLACPlayer,
    }

    @staticmethod
    def create_audio_player(type_: MediaFormat, volume: int, playBackRate: float) -> AudioPlayer:
        try:
            player_cls = AudioPlayerFactory._PLAYERS[type_]
        except (KeyError, TypeError):
            raise ValueError(f"Unsupported media format: {type_!r}") from None
        return player_cls(volume, playBackRate)
