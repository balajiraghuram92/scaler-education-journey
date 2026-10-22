from types import SimpleNamespace

import pytest

from models.enums import GameState
from models.move import Move
from models.player import Player
from models.symbol import Symbol
from services.game_service import GameService
from strategies.winning_strategy_impl import WinningStrategyImpl


def new_game(dimension=3):
    strategy = WinningStrategyImpl()
    service = GameService(strategy)
    x = Player("X-player", Symbol("X"))
    o = Player("O-player", Symbol("O"))
    return service, strategy, service.start_game(dimension, [x, o]), x, o


def play(service, game, cells):
    for r, c in cells:
        service.make_move(game, r, c)


def test_counter_dictionaries_exist():
    s = WinningStrategyImpl()
    for name in ("row_maps", "col_maps", "left_diagonal_map", "right_diagonal_map"):
        assert isinstance(getattr(s, name), dict), f"{name} must be a dict"


def test_row_win():
    service, _, game, x, _ = new_game()
    play(service, game, [(1, 0), (0, 0), (1, 1), (0, 1), (1, 2)])
    assert game.game_state == GameState.ENDED and game.winner is x


def test_column_win():
    service, _, game, x, _ = new_game()
    play(service, game, [(0, 2), (0, 0), (1, 2), (0, 1), (2, 2)])
    assert game.game_state == GameState.ENDED and game.winner is x


def test_main_diagonal_win():
    service, _, game, x, _ = new_game()
    play(service, game, [(0, 0), (0, 1), (1, 1), (0, 2), (2, 2)])
    assert game.game_state == GameState.ENDED and game.winner is x


def test_anti_diagonal_win():
    service, _, game, _, o = new_game()
    play(service, game, [(0, 0), (0, 2), (0, 1), (1, 1), (1, 0), (2, 0)])
    assert game.game_state == GameState.ENDED and game.winner is o


def test_no_false_win_with_mixed_symbols():
    service, _, game, _, _ = new_game()
    play(service, game, [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)])
    # board is X O X / O X O: nobody owns a whole line
    assert game.game_state == GameState.IN_PROGRESS
    assert game.winner is None


def test_check_is_constant_time_and_never_reads_the_grid():
    strategy = WinningStrategyImpl()
    board = SimpleNamespace(dimension=3)  # no grid at all: scanning the board would fail
    p = Player("p", Symbol("X"))
    results = []
    for r, c in [(0, 0), (1, 1), (2, 2)]:
        results.append(strategy.check_winner(board, Move(p, SimpleNamespace(row=r, col=c))))
    assert results == [False, False, True], "three on the main diagonal must win using counters only"


def test_works_on_larger_boards():
    service, _, game, x, _ = new_game(5)
    play(service, game, [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2), (0, 3), (1, 3)])
    assert game.game_state == GameState.IN_PROGRESS, "four in a row is not enough on a 5x5 board"
    service.make_move(game, 0, 4)
    assert game.game_state == GameState.ENDED and game.winner is x


def test_draw_when_board_is_full():
    service, _, game, _, _ = new_game()
    play(service, game, [(0, 0), (0, 1), (0, 2), (1, 1), (1, 0), (1, 2), (2, 1), (2, 0), (2, 2)])
    assert game.game_state == GameState.DRAW
    assert game.winner is None


def test_moves_after_game_end_are_ignored():
    service, _, game, x, _ = new_game()
    play(service, game, [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)])
    assert game.winner is x
    before = len(game.moves)
    service.make_move(game, 2, 2)
    assert len(game.moves) == before
    assert game.winner is x
