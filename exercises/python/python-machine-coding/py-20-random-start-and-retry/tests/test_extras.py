import random

import pytest

from tictactoe.extras import RetryingController, SeededBuilder, TooManyInvalidMovesError
from tictactoe.game import (
    ColumnWinningStrategy,
    DiagonalWinningStrategy,
    Game,
    GameState,
    InvalidGameConfigError,
    RowWinningStrategy,
    ScriptedPlayer,
    Symbol,
)

STRATEGIES = [RowWinningStrategy(), ColumnWinningStrategy(), DiagonalWinningStrategy()]


def two_players(a_moves, b_moves):
    return [ScriptedPlayer("A", Symbol("X"), a_moves), ScriptedPlayer("B", Symbol("O"), b_moves)]


def test_same_seed_gives_same_first_player_and_all_players_still_present():
    controller = RetryingController()
    first = [controller.start_game_seeded(3, two_players([], []), STRATEGIES, random.Random(7)).players[0].name
             for _ in range(3)]
    assert len(set(first)) == 1, "the same seed must always pick the same starter"
    game = controller.start_game_seeded(3, two_players([], []), STRATEGIES, random.Random(7))
    assert sorted(p.name for p in game.players) == ["A", "B"]


def test_both_players_can_start_for_some_seed():
    controller = RetryingController()
    starters = {controller.start_game_seeded(3, two_players([], []), STRATEGIES, random.Random(s)).players[0].name
                for s in range(30)}
    assert starters == {"A", "B"}, "over many seeds each player must be able to start"


def test_rotation_preserves_turn_order():
    controller = RetryingController()
    seen = set()
    for seed in range(40):
        players = [ScriptedPlayer(n, Symbol(n), []) for n in "ABC"]
        game = controller.start_game_seeded(4, players, STRATEGIES, random.Random(seed))
        order = "".join(p.name for p in game.players)
        assert order in ("ABC", "BCA", "CAB"), f"turn order must be a rotation, got {order}"
        seen.add(order)
    assert seen == {"ABC", "BCA", "CAB"}


def test_builder_keeps_existing_validation():
    builder = SeededBuilder(random.Random(1))
    assert isinstance(builder, Game.Builder)
    builder.set_dimension(2).add_winning_strategy(RowWinningStrategy())
    with pytest.raises(InvalidGameConfigError):
        builder.build()
    dup = SeededBuilder(random.Random(1)).set_dimension(3)
    dup.add_player(ScriptedPlayer("A", Symbol("X"), [])).add_player(ScriptedPlayer("B", Symbol("X"), []))
    dup.add_winning_strategy(RowWinningStrategy())
    with pytest.raises(InvalidGameConfigError):
        dup.build()


def test_play_retries_an_invalid_move_and_finishes():
    controller = RetryingController()
    players = two_players([(0, 0), (0, 1), (0, 2)], [(0, 0), (1, 0), (1, 1)])  # B first tries the taken (0, 0)
    game = controller.play(controller.start_game(3, players, STRATEGIES))
    assert game.state is GameState.ENDED
    assert game.winner.name == "A"
    assert len(game.moves) == 5


def test_invalid_counter_resets_after_a_valid_move():
    controller = RetryingController()
    a = [(0, 0), (0, 0), (1, 0), (0, 1), (0, 2)]
    # A: valid (0,0); later two invalid ((0,0),(1,0) taken by B) then valid (0,1); then (0,2) wins
    b = [(0, 0), (0, 0), (1, 0), (1, 1)]  # B: two invalid, valid (1,0); later valid (1,1)
    game = controller.start_game(3, two_players(a, b), STRATEGIES)
    controller.play(game, max_invalid_moves=2)
    assert game.state is GameState.ENDED and game.winner.name == "A", "two streaks of 2 must be allowed with max 2"


def test_play_gives_up_after_too_many_invalid_moves():
    controller = RetryingController()
    game = controller.start_game(3, two_players([(0, 0)], [(0, 0)] * 5), STRATEGIES)
    with pytest.raises(TooManyInvalidMovesError):
        controller.play(game, max_invalid_moves=2)
    assert len(game.moves) == 1, "no extra move may be recorded"
    assert game.state is GameState.IN_PROGRESS
    assert game.players[game.next_player_index].name == "B", "it is still B's turn"


def test_too_many_error_is_chain_suppressed():
    controller = RetryingController()
    game = controller.start_game(3, two_players([(0, 0)], [(0, 0)] * 5), STRATEGIES)
    with pytest.raises(TooManyInvalidMovesError) as info:
        controller.play(game, max_invalid_moves=1)
    assert info.value.__suppress_context__ is True, "raise ... from None"


def test_play_runs_a_game_to_a_draw():
    controller = RetryingController()
    a = [(0, 0), (0, 2), (1, 0), (2, 1), (2, 2)]
    b = [(0, 1), (1, 1), (1, 2), (2, 0)]
    game = controller.play(controller.start_game(3, two_players(a, b), STRATEGIES))
    assert game.state is GameState.DRAW
    assert game.winner is None
    assert len(game.moves) == 9


def test_play_on_finished_game_returns_immediately():
    controller = RetryingController()
    players = two_players([(0, 0), (0, 1), (0, 2)], [(1, 0), (1, 1)])
    game = controller.play(controller.start_game(3, players, STRATEGIES))
    moves = len(game.moves)
    again = controller.play(game)
    assert again is game
    assert len(game.moves) == moves
