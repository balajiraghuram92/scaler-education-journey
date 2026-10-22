import pytest

from controllers.game_controller import GameController
from exceptions.exceptions import EmptyMovesException
from models.enums import CellState, GameState
from models.player import Player
from models.symbol import Symbol
from services.game_service import GameService
from strategies.winning_strategy_impl import WinningStrategyImpl


@pytest.fixture
def setup():
    strategy = WinningStrategyImpl()
    service = GameService(strategy)
    x = Player("X-player", Symbol("X"))
    o = Player("O-player", Symbol("O"))
    game = service.start_game(3, [x, o])
    return service, strategy, game, x, o


def play(service, game, cells):
    for r, c in cells:
        service.make_move(game, r, c)


def test_undo_with_no_moves_raises(setup):
    service, _, game, _, _ = setup
    with pytest.raises(EmptyMovesException):
        service.undo(game)


def test_undo_empties_the_cell_and_pops_the_move(setup):
    service, _, game, x, _ = setup
    play(service, game, [(0, 0), (1, 1)])
    service.undo(game)
    cell = game.board.board[1][1]
    assert cell.cell_state == CellState.EMPTY
    assert cell.player is None, "the undone cell must have no player"
    assert len(game.moves) == 1
    assert game.board.board[0][0].player is x, "earlier moves stay"


def test_undo_gives_the_turn_back(setup):
    service, _, game, x, o = setup
    play(service, game, [(0, 0), (1, 1), (2, 2)])
    assert game.players[game.next_player_move_index] is o
    service.undo(game)
    assert game.players[game.next_player_move_index] is x, "X made the undone move so X plays again"
    service.undo(game)
    assert game.players[game.next_player_move_index] is o
    service.undo(game)
    assert game.players[game.next_player_move_index] is x
    assert game.next_player_move_index == 0, "wraps back to the first player"


def test_undo_after_win_resumes_game(setup):
    service, _, game, x, _ = setup
    play(service, game, [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)])
    assert game.game_state == GameState.ENDED and game.winner is x
    service.undo(game)
    assert game.game_state == GameState.IN_PROGRESS
    assert game.winner is None
    service.make_move(game, 2, 2)  # the game accepts moves again
    assert len(game.moves) == 5


def test_undo_after_draw_resumes_game(setup):
    service, _, game, _, _ = setup
    play(service, game, [(0, 0), (0, 1), (0, 2), (1, 1), (1, 0), (1, 2), (2, 1), (2, 0), (2, 2)])
    assert game.game_state == GameState.DRAW
    service.undo(game)
    assert game.game_state == GameState.IN_PROGRESS
    assert game.winner is None
    assert len(game.moves) == 8


def test_undone_move_does_not_count_towards_a_win(setup):
    service, _, game, _, _ = setup
    play(service, game, [(0, 0), (1, 0), (0, 1)])
    service.undo(game)  # X's (0,1) is gone, X to move
    play(service, game, [(2, 2), (1, 1), (0, 2)])  # X holds (0,0),(2,2),(0,2): row 0 is NOT complete
    assert game.game_state == GameState.IN_PROGRESS, "an undone move must not count towards row 0"
    assert game.winner is None


def test_handle_undo_decrements_counters(setup):
    service, strategy, game, x, _ = setup
    play(service, game, [(0, 0), (1, 0), (1, 1), (2, 0), (2, 2)])  # X on both main-diagonal cells etc.
    sym = x.symbol
    assert strategy.left_diagonal_map[sym] == 3
    before_row = strategy.row_maps[1][sym]
    before_col = strategy.col_maps[1][sym]
    before_left = strategy.left_diagonal_map[sym]
    strategy.handle_undo(game.board, game.moves[2])  # the (1,1) move: row 1, col 1, both diagonals
    assert strategy.row_maps[1][sym] == before_row - 1
    assert strategy.col_maps[1][sym] == before_col - 1
    assert strategy.left_diagonal_map[sym] == before_left - 1
    assert strategy.right_diagonal_map[sym] == 0, "(1,1) lies on the right diagonal too, X had only that one"


def test_undo_everything_then_replay(setup):
    service, strategy, game, x, o = setup
    moves = [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)]
    play(service, game, moves)
    for _ in moves:
        service.undo(game)
    assert game.moves == []
    assert all(c.cell_state == CellState.EMPTY for row in game.board.board for c in row)
    assert game.game_state == GameState.IN_PROGRESS
    assert all(v == 0 for m in strategy.row_maps.values() for v in m.values()), "row counters must return to zero"
    play(service, game, moves)
    assert game.game_state == GameState.ENDED and game.winner is x


def test_controller_delegates_undo(setup):
    service, _, game, _, _ = setup
    controller = GameController(service)
    controller.make_move(game, 0, 0)
    controller.undo(game)
    assert game.moves == []
    with pytest.raises(EmptyMovesException):
        controller.undo(game)
