import pytest

from config.abstract_factory import AudioFactory, FLACAudioFactory, MP3AudioFactory
from config.decoder import AudioDecoder, FLACDecoder, MP3Decoder
from config.model import MediaFormat
from config.player import AudioPlayer, FLACPlayer, MP3Player
from config.processor import AudioProcessor, FLACAudioProcessor, MP3AudioProcessor

FAMILIES = [
    (MP3AudioFactory, MediaFormat.MP3, MP3Player, MP3Decoder, MP3AudioProcessor),
    (FLACAudioFactory, MediaFormat.FLAC, FLACPlayer, FLACDecoder, FLACAudioProcessor),
]
IDS = ["mp3", "flac"]


def test_audio_factory_is_abstract_with_four_abstract_methods():
    with pytest.raises(TypeError):
        AudioFactory()
    assert AudioFactory.__abstractmethods__ == {
        "supports_format",
        "create_audio_player",
        "create_audio_decoder",
        "create_audio_processor",
    }, f"abstract methods found: {sorted(AudioFactory.__abstractmethods__)}"


@pytest.mark.parametrize("factory_cls, fmt, player, decoder, processor", FAMILIES, ids=IDS)
def test_concrete_factories_are_instantiable_and_report_their_format(factory_cls, fmt, player, decoder, processor):
    assert issubclass(factory_cls, AudioFactory)
    assert factory_cls().supports_format() is fmt


@pytest.mark.parametrize("factory_cls, fmt, player, decoder, processor", FAMILIES, ids=IDS)
def test_factory_creates_the_concrete_products_of_its_family(factory_cls, fmt, player, decoder, processor):
    factory = factory_cls()
    assert type(factory.create_audio_player(50, 1.0)) is player
    assert type(factory.create_audio_decoder(b"x")) is decoder
    assert type(factory.create_audio_processor(b"x")) is processor


@pytest.mark.parametrize("factory_cls, fmt, player, decoder, processor", FAMILIES, ids=IDS)
def test_products_share_the_common_abstract_parents(factory_cls, fmt, player, decoder, processor):
    factory = factory_cls()
    assert isinstance(factory.create_audio_player(50, 1.0), AudioPlayer)
    assert isinstance(factory.create_audio_decoder(b"x"), AudioDecoder)
    assert isinstance(factory.create_audio_processor(b"x"), AudioProcessor)


@pytest.mark.parametrize("factory_cls, fmt, player, decoder, processor", FAMILIES, ids=IDS)
def test_every_product_matches_the_factorys_format(factory_cls, fmt, player, decoder, processor):
    factory = factory_cls()
    products = [
        factory.create_audio_player(10, 1.0),
        factory.create_audio_decoder(b"data"),
        factory.create_audio_processor(b"data"),
    ]
    assert [p.supports_format() for p in products] == [fmt] * 3, "all three products must come from the same family"


def test_constructor_arguments_reach_the_products():
    factory = MP3AudioFactory()
    p = factory.create_audio_player(70, 1.5)
    assert (p.volume, p.playback_rate) == (70, 1.5)
    assert factory.create_audio_decoder(b"abc").audio_data == b"abc"
    assert factory.create_audio_processor(b"xyz").audio_data == b"xyz"


def test_each_call_creates_a_new_product():
    factory = FLACAudioFactory()
    assert factory.create_audio_player(1, 1.0) is not factory.create_audio_player(1, 1.0)
    assert factory.create_audio_decoder(b"a") is not factory.create_audio_decoder(b"a")


def test_client_code_depends_only_on_the_abstract_factory():
    def build_pipeline(factory: AudioFactory):
        return {
            factory.create_audio_player(5, 1.0).supports_format(),
            factory.create_audio_decoder(b"d").supports_format(),
            factory.create_audio_processor(b"d").supports_format(),
        }

    for factory_cls, fmt, *_ in FAMILIES:
        assert build_pipeline(factory_cls()) == {fmt}, "a pipeline built from one factory must not mix formats"
