import pytest

from audio.factory import AudioPlayerFactory
from audio.products import AudioPlayer, FLACPlayer, MediaFormat, MP3Player, WAVPlayer

EXPECTED = {MediaFormat.MP3: MP3Player, MediaFormat.WAV: WAVPlayer, MediaFormat.FLAC: FLACPlayer}


@pytest.mark.parametrize("fmt", list(MediaFormat))
def test_factory_returns_the_right_concrete_type(fmt):
    player = AudioPlayerFactory.create_audio_player(fmt, 50, 1.0)
    assert type(player) is EXPECTED[fmt], f"{fmt} should produce {EXPECTED[fmt].__name__}"
    assert isinstance(player, AudioPlayer)
    assert player.supports_type() is fmt


def test_factory_passes_volume_and_playback_rate():
    player = AudioPlayerFactory.create_audio_player(MediaFormat.WAV, 70, 1.5)
    assert player.volume == 70 and player.playBackRate == 1.5


def test_create_audio_player_is_a_static_method():
    assert AudioPlayerFactory.create_audio_player(MediaFormat.MP3, 1, 1.0) is not None
    assert isinstance(AudioPlayerFactory.__dict__["create_audio_player"], staticmethod), "use @staticmethod"


def test_unknown_format_raises_value_error():
    with pytest.raises(ValueError):
        AudioPlayerFactory.create_audio_player("ogg", 50, 1.0)
    with pytest.raises(ValueError):
        AudioPlayerFactory.create_audio_player(None, 50, 1.0)


def test_every_supported_format_works_through_the_abstract_interface(capsys):
    for fmt in MediaFormat:
        player = AudioPlayerFactory.create_audio_player(fmt, 10, 1.0)
        player.play()
        player.pause()
        player.stop()
    out = capsys.readouterr().out
    for fmt in MediaFormat:
        assert fmt.name in out, f"{fmt.name} player should print something mentioning its format"


@pytest.mark.parametrize("fmt, text", [(MediaFormat.MP3, "Playing MP3 audio"), (MediaFormat.WAV, "Playing WAV audio"), (MediaFormat.FLAC, "Playing FLAC audio")])
def test_play_prints_the_format_specific_line(capsys, fmt, text):
    AudioPlayerFactory.create_audio_player(fmt, 10, 1.0).play()
    assert text in capsys.readouterr().out


def test_set_volume_accepts_0_to_100_and_rejects_the_rest(capsys):
    player = AudioPlayerFactory.create_audio_player(MediaFormat.MP3, 50, 1.0)
    for ok in (0, 100, 33):
        player.set_volume(ok)
        assert player.volume == ok
    capsys.readouterr()
    for bad in (-1, 101):
        player.set_volume(bad)
        assert player.volume == 33, f"{bad} is invalid and must leave the volume unchanged"
        assert "nvalid" in capsys.readouterr().out, "an invalid level must be reported"


def test_audio_player_base_is_abstract():
    with pytest.raises(TypeError):
        AudioPlayer(50, 1.0)


def test_factory_builds_only_the_selected_player(monkeypatch):
    built = []
    for cls in (MP3Player, WAVPlayer, FLACPlayer):
        original = cls.__init__

        def tracking_init(self, *a, __orig=original, **k):
            built.append(type(self))
            __orig(self, *a, **k)

        monkeypatch.setattr(cls, "__init__", tracking_init)
    AudioPlayerFactory.create_audio_player(MediaFormat.FLAC, 1, 1.0)
    assert built == [FLACPlayer], f"only the requested product may be constructed, built: {built}"
