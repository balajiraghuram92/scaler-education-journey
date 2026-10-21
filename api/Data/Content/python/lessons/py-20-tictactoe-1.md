# Code TicTacToe 1: Design and Core Game Loop

TicTacToe is the canonical first machine-coding problem because the rules are trivial and everything else is not: the order you write classes in, where validation lives, and whether the thing runs at minute forty. Interviewers use it to see whether you can turn a diagram into small, importable classes and a game loop that works, while explaining each decision aloud. This lesson builds the design and the core move loop; the next one makes the win check O(1) and adds bots and undo.

## Concepts Covered

### Requirements, and what you leave out

Machine coding starts exactly like the design round: align, then agree requirements. For TicTacToe the agreed list is below. Note that two items are deferred on purpose, because naming what you skip is part of the answer.

| ID | Requirement | Becomes |
|---|---|---|
| FR-1 | Square N x N board, N chosen at start | `Board(dimension)`, `Cell` |
| FR-2 | Exactly N - 1 players | validation in the Builder |
| FR-3 | Each player picks a unique symbol | `Symbol`, uniqueness check |
| FR-4 | A player may be a bot with a difficulty | `Player.player_type`, bots in the next lesson |
| FR-5 | Players move in turns; a move names an in-bounds empty cell | `Player.make_move`, `Game.make_move`, `InvalidMoveError` |
| FR-6 | After every move check for a winner (row, column, diagonal) | `WinningStrategy` and three subclasses |
| FR-7 | The game ends with a winner or a draw | `GameState`, `Game.winner` |
| FR-8 | Win check must not rescan the whole board | O(N) here, O(1) next lesson |
| FR-9, FR-10 | Random first player, undo | deferred; keep `Game.moves` so undo stays possible |

Out of scope: tournaments, leaderboards, time per move, hints. Non-functional: an interactive console program, in memory, no persistence.

### Seven alignment questions, answered

Players on a 3 x 3 board? N - 1, which is two. Because the rule spans two settings (dimension and player count), `Game` is created through a **Builder** whose `build()` validates everything at once and raises `InvalidGameConfigError` before any `Game` exists. Who runs a turn? `Game` does: ask the player, validate, update, switch, check. `Board` knows cells, `Player` only decides, and `GameController` is a front door. The winning rules are a **Strategy**: an abstract class with one small class per rule, so a new rule is a new file and zero edits to `Game`. A bot is a `Player` subclass that overrides `make_move`, so `Game` never asks "are you a bot?". Finally, `Game` composes a `Board` (created inside `__init__`) and merely aggregates its `Player`s (they come from outside and may play again).

### The class diagram

```text
 GameController --> Game 1 <>--- 1 Board 1 <>--- * Cell
                     |  \            
                     |   o--- * Player <|-- Bot (next lesson)
                     |   <>-- * Move (player, cell)
                     |   o--- * WinningStrategy <|-- Row, Column, Diagonal
 Game.state : GameState {IN_PROGRESS, ENDED, DRAW}
 Cell.state : CellState {EMPTY, FILLED}     Cell.player : Player | None
 Symbol(char)   PlayerType {HUMAN, BOT}
```

Two small decisions are worth saying aloud. `Cell` stores a `player`, not a duplicate `symbol`, because the symbol is reachable as `cell.player.symbol` and two copies could disagree. And a state is an `Enum`, never a string or a bare boolean: `CellState.EMPTY` is readable, and a typo is a loud `AttributeError` rather than a silently false comparison.

### Build order: leaves before roots

A file may only import things built before it, so write classes that import nothing first, the integrating `Game` late, and the entry point last. If time runs short, skip optional stages and you still have a playable game.

| Stage | What | Time box |
|---|---|---|
| S1 | enums, `Symbol`, exceptions | 10 min |
| S2 | `Cell`, `Board` | 12 min |
| S3 | `Move`, `Player` | 10 min |
| S4 | `WinningStrategy` and subclasses | 15 min |
| S5 | `Game`, Builder, `GameController`, demo | 25 min |

### Stages 1 to 3: leaves, board, people

`Symbol` is a frozen dataclass, so it is hashable and compares by character, which makes "unique symbols" a one-line set comprehension. `Player.make_move` returns a `Move` and never writes to the board: the player decides, `Game` applies. The human reads input through an injectable `reader` (defaulting to `input`), and `ScriptedPlayer` is the same interface fed from a list, which is how you test a console game without a keyboard. Putting `input()` inside a model is acceptable in a 90-minute round if you say you would inject it in a larger system, which is what the `reader` parameter already does.

```python
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
```

The `Cell` inside a human's `Move` is a fresh object with the same coordinates, not the board's cell. `Game` reads only `row` and `col` from it and then touches `board.grid[row][col]`. Remember this asymmetry when you add bots next lesson.

### Stage 4: winning strategies

After a move only the row, column and diagonals through that cell can have changed, so each strategy checks just its line. This is O(N) per move rather than a full-board rescan, and it keeps each rule in its own class.

```python
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
```

The diagonal strategy uses two independent `if` statements, not `if/elif`, because on an odd board the centre cell lies on both diagonals.

### Stage 5: Game, Builder and controller

`Game.make_move()` takes no arguments: the game asks the current player, so `main` never needs to know whose turn it is or how a bot decides. It runs in five steps: ask, validate or raise, fill the real cell, log the move and advance the turn (modulo the player count), then decide the outcome. Validation happens before the turn advances; otherwise a rejected move would silently skip a player. The `Builder` is nested in `Game`, each setter returns `self`, and `build()` collects every problem instead of failing on the first.

```python
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
```

Run it end to end with scripted players, including a bad configuration:

```python
X, O = Symbol("X"), Symbol("O")
strategies = [RowWinningStrategy(), ColumnWinningStrategy(), DiagonalWinningStrategy()]
controller = GameController()

alice = ScriptedPlayer("Alice", X, [(0, 0), (1, 1), (2, 2)])
bob = ScriptedPlayer("Bob", O, [(0, 1), (0, 2)])
game = controller.start_game(3, [alice, bob], strategies)
while game.state is GameState.IN_PROGRESS:
    controller.make_move(game)
controller.print_board(game)
print(game.state.name, game.winner.name)

try:
    controller.start_game(3, [alice, bob, ScriptedPlayer("Cy", X, [])], strategies)
except InvalidGameConfigError as exc:
    print("config error:", exc)
```

```text
X O O
- X -
- - X
ENDED Alice
config error: need exactly 2 players, got 3; every player needs a unique symbol
```

### Tests that pin the behaviour

```python
import pytest


def make_game(alice_moves, bob_moves):
    players = [ScriptedPlayer("Alice", Symbol("X"), alice_moves),
               ScriptedPlayer("Bob", Symbol("O"), bob_moves)]
    return GameController().start_game(3, players, strategies)


def play_out(game: Game) -> Game:
    while game.state is GameState.IN_PROGRESS:
        game.make_move()
    return game


def test_column_win() -> None:
    game = play_out(make_game([(0, 0), (1, 0), (2, 0)], [(0, 1), (1, 1)]))
    assert game.state is GameState.ENDED and game.winner.name == "Alice"


def test_draw_when_board_fills() -> None:
    alice = [(0, 0), (0, 2), (1, 0), (2, 1), (2, 2)]
    bob = [(0, 1), (1, 1), (1, 2), (2, 0)]
    game = play_out(make_game(alice, bob))
    assert game.state is GameState.DRAW and game.winner is None


def test_invalid_move_does_not_advance_the_turn() -> None:
    game = make_game([(0, 0)], [(0, 0), (1, 1)])
    game.make_move()                      # Alice takes (0, 0)
    with pytest.raises(InvalidMoveError):
        game.make_move()                  # Bob tries the same cell
    assert game.next_player_index == 1 and len(game.moves) == 1
    game.make_move()                      # Bob retries with (1, 1)
    assert game.moves[-1].player.name == "Bob"


def test_move_after_game_over_is_rejected() -> None:
    game = play_out(make_game([(0, 0), (0, 1), (0, 2)], [(1, 0), (1, 1)]))
    with pytest.raises(GameOverError):
        game.make_move()


def test_builder_reports_every_problem_at_once() -> None:
    with pytest.raises(InvalidGameConfigError) as info:
        Game.builder().set_dimension(2).build()
    assert "dimension" in str(info.value) and "winning strategy" in str(info.value)
```

All five pass against the code above.

### Gaps to say out loud

Real interviewers appreciate honesty about what is unfinished. A human move that is out of bounds raises and, with a console `reader`, crashes the demo; a retry loop around `make_move` is the fix. The first player is always `players[0]`, undo is not implemented, and there are no bots yet. Name these before the interviewer does.

## Practical Backend Scenario

You are asked to build a small rules engine for an LLM evaluation harness: a "match" between two model answers is judged by several checks (length, citation, safety), and a match ends when any check decides. The structure is the same: a `Match` aggregate that owns the loop, a `Check` strategy per rule so a new rule is a new class, a Builder that rejects invalid configuration before a run starts (duplicate check names, missing judge), and a scripted judge used in tests instead of a live model. The TicTacToe skeleton, with players replaced by judges, is the whole design.

## Practice Loop

1. Create the package layout (`models`, `strategies`, `controllers`, `exceptions`) with empty `__init__.py` files, and build stages S1 to S3 from memory, running a three-line script after each.
2. Add the three winning strategies and confirm each by hand: a row win, a column win, and both diagonals on a 3 x 3 and a 4 x 4 board with three players.
3. Implement `Game`, the Builder and the controller. Verify that three players on a 3 x 3 board raises `InvalidGameConfigError` and that no `Game` object is created.
4. Write the five tests above using `ScriptedPlayer`. Add one for an out-of-bounds move.
5. Replace the crash on invalid console input with a retry loop that catches `InvalidMoveError` and asks the same player again.
6. Time yourself: stages S1 to S5 plus tests within 90 minutes, narrating each decision aloud.

## Evidence of Understanding

- I can list the agreed requirements and say which two I deferred and why.
- I can explain why `Game` is created through a Builder and why `build()` collects all problems.
- I can state why `Player.make_move` returns a `Move` and never writes to the board.
- I can explain why validation must run before the turn index advances.
- I can say why the diagonal strategy uses two `if` statements instead of `if/elif`.
- I can explain why `Cell` stores a player rather than a symbol, and why states are enums.
- I can name three known gaps in my solution and how I would close each.

## Interview Questions to Rehearse

### Q: Why use a Builder for `Game` instead of keyword arguments?

The configuration has cross-field rules: player count depends on dimension, and symbols must be unique across players. A Builder gathers the parts and validates them together in `build()`, so no invalid `Game` can exist. Keyword arguments are fine when fields are independent. Here, I would also point out that a Builder gives readable construction and a single place for validation, and that I would not use it for a three-field value object.

### Q: How do you keep the winning logic out of `Game`?

Behind a `WinningStrategy` abstract class with one subclass per rule. `Game` holds a list and asks each whether the last move won. A new rule, such as a corner win, is one new class and no edit to `Game`, which is the open-closed principle in practice. The trade-off is a little indirection, which is justified because rules are the likeliest requirement to change.

### Q: A human types an occupied cell. What should happen?

`Game._validate` raises `InvalidMoveError` before changing any state, and the turn index has not advanced, so the same player is asked again. The caller decides policy: a console loop retries, a network API returns an error response. Raising a named exception, instead of printing "invalid" and returning, keeps rules separate from presentation.

### Q: Why does `make_move` take no arguments?

Because the game owns whose turn it is. If `make_move(row, col)` took arguments, the caller would need to know the current player and how a bot decides. Asking `players[next_player_index]` for a `Move` lets humans and bots share one interface, and `main` becomes a loop that calls `game.make_move()` until the state changes.

### Q: What would you change if this had to serve many concurrent games?

I would remove `input()` from models entirely, make `Game` own no global state (it already does not), identify games by id in a repository, and guard each game's `make_move` with a per-game lock or serialise moves through a queue. Winning strategies must not be shared between games once they hold counters, which is a real hazard when they become stateful in the next lesson.

## Common Pitfalls

- Starting with the bot or the AI difficulty levels, and having no playable game at minute forty.
- A setter that forgets `return self`, so the fluent chain raises `AttributeError` on `None`.
- Advancing `next_player_index` before validating, which skips a player after a rejected move.
- Building the grid as `[["-"] * n] * n`, which repeats one row object; use a comprehension that builds fresh cells.
- Keeping both `cell.symbol` and `cell.player`, then letting them disagree.
- Using `if/elif` for the two diagonals and missing the centre cell on odd boards.
- Reading `move.cell.state` in a strategy: a human's `Move` carries a fresh cell, so read `row`, `col` and `move.player.symbol` instead.
- Magic strings such as `"empty"` instead of `CellState.EMPTY`, where a typo is silently false.

## Suggested Extension

Implement requirement FR-9, a random first player, and decide where it belongs. One option is the Builder (shuffle the list when `build()` is called) and another is `Game.__init__`. Argue for one, make it deterministic in tests by injecting a `random.Random` seeded in the test, and add a test that the same seed always produces the same starting player.
