from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum


class CellState(Enum):
    EMPTY = "empty"
    FILLED = "filled"


class GameState(Enum):
    IN_PROGRESS = "in_progress"
    ENDED = "ended"
    DRAW = "draw"


class PlayerType(Enum):
    HUMAN = "human"
    BOT = "bot"


@dataclass(frozen=True)
class Symbol:
    char: str

    def __post_init__(self) -> None:
        if len(self.char) != 1:
            raise ValueError("a symbol is exactly one character")


class InvalidMoveError(Exception):
    """The move names a cell that is out of bounds or already filled."""


class InvalidGameConfigError(Exception):
    """The Builder refused to create a Game; the message lists every problem."""


class GameOverError(Exception):
    """A move was attempted on a game that has already ended."""


class Cell:
    def __init__(self, row: int, col: int) -> None:
        self.row = row
        self.col = col
        self.state = CellState.EMPTY
        self.player: Player | None = None      # symbol is reachable as cell.player.symbol


class Board:
    """Storage and display only. Rules live elsewhere."""

    def __init__(self, dimension: int) -> None:
        self.dimension = dimension
        self.grid = [[Cell(r, c) for c in range(dimension)] for r in range(dimension)]

    def render(self) -> str:
        return "\n".join(
            " ".join(c.player.symbol.char if c.player else "-" for c in row) for row in self.grid
        )


@dataclass(frozen=True)
class Move:
    player: Player
    cell: Cell


class Player:
    def __init__(self, name: str, symbol: Symbol, player_type: PlayerType = PlayerType.HUMAN,
                 reader: Callable[[str], str] = input) -> None:
        self.name = name
        self.symbol = symbol
        self.player_type = player_type
        self._reader = reader

    def make_move(self, board: Board) -> Move:
        """Decide; never touch the board. Game validates and applies."""
        row, col = (int(x) for x in self._reader(f"{self.name} ({self.symbol.char}) row col: ").split())
        return Move(self, Cell(row, col))          # a fresh Cell: only its coordinates matter


class ScriptedPlayer(Player):
    """Same interface, no keyboard: the test double for input()."""

    def __init__(self, name: str, symbol: Symbol, script: list[tuple[int, int]]) -> None:
        super().__init__(name, symbol)
        self._script = list(script)

    def make_move(self, board: Board) -> Move:
        row, col = self._script.pop(0)
        return Move(self, Cell(row, col))

class WinningStrategy(ABC):
    @abstractmethod
    def check_winner(self, board: Board, move: Move) -> bool: ...

    def handle_undo(self, board: Board, move: Move) -> None:
        """Hook for undo (next lesson). Stateless strategies have nothing to roll back."""


def _all_owned_by(cells: list[Cell], symbol: Symbol) -> bool:
    return all(c.state is CellState.FILLED and c.player.symbol == symbol for c in cells)


class RowWinningStrategy(WinningStrategy):
    def check_winner(self, board: Board, move: Move) -> bool:
        return _all_owned_by(board.grid[move.cell.row], move.player.symbol)


class ColumnWinningStrategy(WinningStrategy):
    def check_winner(self, board: Board, move: Move) -> bool:
        column = [row[move.cell.col] for row in board.grid]
        return _all_owned_by(column, move.player.symbol)


class DiagonalWinningStrategy(WinningStrategy):
    def check_winner(self, board: Board, move: Move) -> bool:
        n, r, c = board.dimension, move.cell.row, move.cell.col
        if r == c and _all_owned_by([board.grid[i][i] for i in range(n)], move.player.symbol):
            return True
        if r + c == n - 1 and _all_owned_by([board.grid[i][n - 1 - i] for i in range(n)], move.player.symbol):
            return True
        return False

class Game:
    def __init__(self, dimension: int, players: list[Player],
                 winning_strategies: list[WinningStrategy]) -> None:
        self.board = Board(dimension)
        self.players = players
        self.winning_strategies = winning_strategies
        self.moves: list[Move] = []
        self.next_player_index = 0
        self.state = GameState.IN_PROGRESS
        self.winner: Player | None = None

    @staticmethod
    def builder() -> Game.Builder:
        return Game.Builder()

    class Builder:
        def __init__(self) -> None:
            self._dimension = 0
            self._players: list[Player] = []
            self._strategies: list[WinningStrategy] = []

        def set_dimension(self, dimension: int) -> Game.Builder:
            self._dimension = dimension
            return self                                  # without "return self" the chain breaks

        def add_player(self, player: Player) -> Game.Builder:
            self._players.append(player)
            return self

        def add_winning_strategy(self, strategy: WinningStrategy) -> Game.Builder:
            self._strategies.append(strategy)
            return self

        def build(self) -> Game:
            problems = []
            if self._dimension < 3:
                problems.append("dimension must be at least 3")
            if len(self._players) != self._dimension - 1:
                problems.append(f"need exactly {self._dimension - 1} players, got {len(self._players)}")
            if len({p.symbol for p in self._players}) != len(self._players):
                problems.append("every player needs a unique symbol")
            if not self._strategies:
                problems.append("at least one winning strategy is required")
            if problems:
                raise InvalidGameConfigError("; ".join(problems))
            return Game(self._dimension, self._players, self._strategies)

    def make_move(self) -> None:
        if self.state is not GameState.IN_PROGRESS:
            raise GameOverError("the game is already over")
        player = self.players[self.next_player_index]
        requested = player.make_move(self.board)                         # 1. ask the current player
        cell = self._validate(requested.cell.row, requested.cell.col)    # 2. validate or raise
        cell.state, cell.player = CellState.FILLED, player               # 3. fill the real cell
        move = Move(player, cell)
        self.moves.append(move)                                          # 4. log, then advance
        self.next_player_index = (self.next_player_index + 1) % len(self.players)
        if self._has_winner(move):                                       # 5. outcome
            self.state, self.winner = GameState.ENDED, player
        elif len(self.moves) == self.board.dimension ** 2:
            self.state = GameState.DRAW

    def _has_winner(self, move: Move) -> bool:
        return any(s.check_winner(self.board, move) for s in self.winning_strategies)

    def _validate(self, row: int, col: int) -> Cell:
        n = self.board.dimension
        if not (0 <= row < n and 0 <= col < n):
            raise InvalidMoveError(f"({row}, {col}) is outside the board")
        cell = self.board.grid[row][col]
        if cell.state is CellState.FILLED:
            raise InvalidMoveError(f"({row}, {col}) is already taken")
        return cell


class GameController:
    """A one-line front door: no rules here."""

    def start_game(self, dimension: int, players: list[Player],
                   strategies: list[WinningStrategy]) -> Game:
        builder = Game.builder().set_dimension(dimension)
        for p in players:
            builder.add_player(p)
        for s in strategies:
            builder.add_winning_strategy(s)
        return builder.build()

    def make_move(self, game: Game) -> None:
        game.make_move()

    def print_board(self, game: Game) -> None:
        print(game.board.render())
