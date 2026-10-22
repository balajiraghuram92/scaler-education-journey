import pytest

from board_game import BoardGame
from board_game_factory import BoardGameFactory
from game_type import GameType
from games.chess_board_game import ChessBoardGame
from games.snake_ladder_board_game import SnakeLadderBoardGame
from games.tic_tac_toe_board_game import TicTacToeBoardGame

EXPECTED = {
    GameType.TIC_TAC_TOE: TicTacToeBoardGame,
    GameType.CHESS: ChessBoardGame,
    GameType.SNAKE_LADDER: SnakeLadderBoardGame,
}


@pytest.mark.parametrize("game_type", list(GameType))
def test_factory_creates_each_game_type(game_type):
    game = BoardGameFactory.create_board_game(game_type, "g")
    assert type(game) is EXPECTED[game_type], f"{game_type} should create {EXPECTED[game_type].__name__}"
    assert isinstance(game, BoardGame)


@pytest.mark.parametrize("game_type", list(GameType))
def test_created_game_reports_its_type(game_type):
    assert BoardGameFactory.create_board_game(game_type, "g").game_type() is game_type


def test_name_is_stored_by_the_parent():
    game = BoardGameFactory.create_board_game(GameType.CHESS, "Club Chess")
    assert game.get_board_game_name() == "Club Chess"
    assert game.board_game_name == "Club Chess"


@pytest.mark.parametrize("bad", [None, "CHESS", 99, object()])
def test_unknown_type_raises_value_error(bad):
    with pytest.raises(ValueError):
        BoardGameFactory.create_board_game(bad, "x")


def test_board_game_is_abstract():
    with pytest.raises(TypeError):
        BoardGame("x")
    assert {"play_game", "game_type"} <= set(BoardGame.__abstractmethods__)


def test_incomplete_subclass_cannot_be_instantiated():
    class Half(BoardGame):
        def play_game(self):
            pass

    with pytest.raises(TypeError):
        Half("half")


def test_shared_behaviour_lives_in_the_parent():
    assert "get_board_game_name" not in BoardGame.__abstractmethods__
    for cls in EXPECTED.values():
        assert "get_board_game_name" not in vars(cls), f"{cls.__name__} must inherit the accessor"
        assert "board_game_name" not in vars(cls)
    assert "get_board_game_name" in vars(BoardGame)


@pytest.mark.parametrize("game_type", list(GameType))
def test_each_game_plays(game_type, capsys):
    BoardGameFactory.create_board_game(game_type, "g").play_game()
    assert capsys.readouterr().out.strip() != ""


def test_factory_returns_new_instances():
    a = BoardGameFactory.create_board_game(GameType.CHESS, "a")
    b = BoardGameFactory.create_board_game(GameType.CHESS, "b")
    assert a is not b
    assert (a.get_board_game_name(), b.get_board_game_name()) == ("a", "b")
