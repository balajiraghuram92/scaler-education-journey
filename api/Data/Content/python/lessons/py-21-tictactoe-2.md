# Code TicTacToe 2: Winning Strategies, Bots and Undo

The first TicTacToe lesson ended with a playable game and three promises: a win check with constant work per move, a bot, and undo. These are the standard follow-ups once the basic loop works, and each stresses a different skill: complexity, the Strategy and Factory patterns, and state you must be able to reverse. This lesson builds on the previous classes and shows where a quick implementation quietly goes wrong.

## Concepts Covered

### From O(N^3) to O(1)

The win check runs after every move, so its cost is paid N^2 times per game. Walk down the optimisation ladder aloud in the interview; the reasoning is the answer.

| Approach | Idea | Cost per move |
|---|---|---|
| Brute force | for each player, for each row, for each column, compare to the symbol | O(N^3) |
| Only the mover | only the player who just moved can have won, so skip the others | O(N^2) |
| Only the last move's lines | a win must include the last cell, so check its row, column and diagonals | O(N) |
| Running counts | keep a count per row, column and diagonal and compare to N | O(1) |

The counting trick: every row, column and diagonal gets a counter per symbol. A move increments at most four counters and compares them with N; the structure holds 2N + 2 counters per symbol, far smaller than the board.

The counters must be keyed by **symbol**, not shared per line. With one shared counter per row, X, O, X in a row reads three and declares a false winner; with a counter per (row, symbol), X reads two. A plain dict raises `KeyError` on the first increment, which is why the code uses `defaultdict(lambda: defaultdict(int))`: the outer dict creates a missing row's inner dict, and the inner creates a missing symbol's zero. The diagonals deserve one more sentence: whatever N is, there are only two, identified by `row == col` and `row + col == N - 1`, and they must be two independent `if` statements because the centre of an odd board sits on both.

```python
from collections import defaultdict


class RowCountStrategy(WinningStrategy):
    """One counter per (row, symbol). A move is one increment and one comparison: O(1)."""

    def __init__(self) -> None:
        self._counts: dict[int, dict[Symbol, int]] = defaultdict(lambda: defaultdict(int))

    def check_winner(self, board: Board, move: Move) -> bool:
        counts = self._counts[move.cell.row]
        counts[move.player.symbol] += 1
        return counts[move.player.symbol] == board.dimension

    def handle_undo(self, board: Board, move: Move) -> None:
        self._counts[move.cell.row][move.player.symbol] -= 1


class ColumnCountStrategy(WinningStrategy):
    def __init__(self) -> None:
        self._counts: dict[int, dict[Symbol, int]] = defaultdict(lambda: defaultdict(int))

    def check_winner(self, board: Board, move: Move) -> bool:
        counts = self._counts[move.cell.col]
        counts[move.player.symbol] += 1
        return counts[move.player.symbol] == board.dimension

    def handle_undo(self, board: Board, move: Move) -> None:
        self._counts[move.cell.col][move.player.symbol] -= 1


class DiagonalCountStrategy(WinningStrategy):
    """Whatever N is there are only two diagonals: row == col, and row + col == N - 1."""

    def __init__(self) -> None:
        self._main: dict[Symbol, int] = defaultdict(int)
        self._anti: dict[Symbol, int] = defaultdict(int)

    def check_winner(self, board: Board, move: Move) -> bool:
        n, r, c, s = board.dimension, move.cell.row, move.cell.col, move.player.symbol
        if r == c:                      # two independent ifs: the centre of an odd board is on both
            self._main[s] += 1
        if r + c == n - 1:
            self._anti[s] += 1
        return (r == c and self._main[s] == n) or (r + c == n - 1 and self._anti[s] == n)

    def handle_undo(self, board: Board, move: Move) -> None:
        n, r, c, s = board.dimension, move.cell.row, move.cell.col, move.player.symbol
        if r == c:
            self._main[s] -= 1
        if r + c == n - 1:
            self._anti[s] -= 1
```

Each strategy is still one small class with one rule. The difference is that they are now **stateful**: the counters belong to one game. So a strategy instance must never be shared between games (create a fresh list per game, as the demo does), and every strategy must see every move.

### Undo: a stack of moves, undone by inverse operations

There are two ways to support undo. A snapshot approach stores the complete state after each move and restores it; it is trivially correct but costs O(N^2) memory per move. The inverse approach keeps the stack of moves that `Game` already logs, and reverses the effects of the last one. The inverse approach is O(1) per undo and its cost is that every piece of derived state, here the counters, needs an inverse operation too. That is why `WinningStrategy` carries a `handle_undo` hook: stateless scanning strategies inherit a no-op, stateful ones decrement what they incremented.

Undo has four duties, and forgetting any one is a classic bug. Clear the **real** board cell (the `Move` stored in `moves` carries it, which is why `Game` logs the real cell and not the fresh one a human returns). Hand the turn back with modulo arithmetic: `-1 % n` is non-negative in Python, so wrap-around needs no special case, unlike C or Java. Roll back every strategy. And reset the state: if the game had ended with a win or a draw, undoing a move makes it `IN_PROGRESS` with no winner. Raise a named `EmptyMovesError` when there is nothing to undo.

The evaluation of winners also changes. Lesson 20's `Game` used `any(generator)`, which stops at the first strategy that reports a win. With stateful strategies that is a bug, because the strategies after it never see the move and their counters fall out of sync, and with undo the game can continue. Build the list of results first, then reduce it.

```python
class EmptyMovesError(Exception):
    """Undo was requested but no move has been played."""


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
            return self

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
        requested = player.make_move(self.board)
        cell = self._validate(requested.cell.row, requested.cell.col)
        cell.state, cell.player = CellState.FILLED, player
        move = Move(player, cell)
        self.moves.append(move)
        self.next_player_index = (self.next_player_index + 1) % len(self.players)
        if self._has_winner(move):
            self.state, self.winner = GameState.ENDED, player
        elif len(self.moves) == self.board.dimension ** 2:
            self.state = GameState.DRAW

    def _has_winner(self, move: Move) -> bool:
        # Stateful strategies must all see every move, so build the list first: any() would short-circuit.
        results = [s.check_winner(self.board, move) for s in self.winning_strategies]
        return any(results)

    def undo(self) -> None:
        if not self.moves:
            raise EmptyMovesError("no moves to undo")
        move = self.moves.pop()
        move.cell.state, move.cell.player = CellState.EMPTY, None      # 1. clear the REAL cell
        self.next_player_index = (self.next_player_index - 1) % len(self.players)   # 2. hand the turn back
        for strategy in self.winning_strategies:                       # 3. roll back counters
            strategy.handle_undo(self.board, move)
        self.state, self.winner = GameState.IN_PROGRESS, None          # 4. a finished game resumes

    def _validate(self, row: int, col: int) -> Cell:
        n = self.board.dimension
        if not (0 <= row < n and 0 <= col < n):
            raise InvalidMoveError(f"({row}, {col}) is outside the board")
        cell = self.board.grid[row][col]
        if cell.state is CellState.FILLED:
            raise InvalidMoveError(f"({row}, {col}) is already taken")
        return cell
```

> **Interview tip:** When asked "how would you implement undo?", name both options and the trade-off in one breath: snapshots are simple and cost memory, inverse operations are cheap and require every derived structure to be reversible. Then say which you chose and what you had to add.

### Bots: Strategy plus Factory, and the identity gap

A `Bot` is a `Player` whose `make_move` delegates to a **BotPlayingStrategy**. The difficulty levels are interchangeable behaviours behind one interface, so this is the Strategy pattern a second time; the mapping from level to behaviour lives in a **Factory** so it exists in exactly one place, never as an `if/elif` inside `Bot` or `Game`. `Game` still never asks "are you a bot?".

The easy bot picks the first empty cell. The medium bot wins if it can, blocks if it must, and otherwise takes the first empty cell. To block, a strategy needs to know who "me" is, which is why the strategy method receives the player (`make_move(board, me)`). The first version of this interface took only the board, and the board holds no information about whose turn it is; that is the **identity gap**: an interface one level too thin for the algorithm behind it. The hard bot is a stub that raises `NotImplementedError`, so the factory imports cleanly and the game starts. A minimax bot needs a depth limit beyond 3 x 3, or it will freeze on a 5 x 5 board.

Note that the bot returns a move with the **real** board cell, whereas the human returns a fresh `Cell`. `Game` reads only the coordinates in both cases, so it works, but the asymmetry is exactly the kind of detail that bites later.

```python
class BotDifficultyLevel(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class BotPlayingStrategy(ABC):
    @abstractmethod
    def make_move(self, board: Board, me: Player) -> Move:
        """The strategy is told WHO it plays for: without that, blocking is impossible."""


def _empty_cells(board: Board) -> list[Cell]:
    return [c for row in board.grid for c in row if c.state is CellState.EMPTY]


def _completes_line(board: Board, cell: Cell, symbol: Symbol) -> bool:
    """Would placing `symbol` on `cell` complete a row, column or diagonal?"""
    n, r, c = board.dimension, cell.row, cell.col
    lines = [board.grid[r], [row[c] for row in board.grid]]
    if r == c:
        lines.append([board.grid[i][i] for i in range(n)])
    if r + c == n - 1:
        lines.append([board.grid[i][n - 1 - i] for i in range(n)])
    return any(
        all(x is cell or (x.state is CellState.FILLED and x.player.symbol == symbol) for x in line)
        for line in lines
    )


class EasyBotPlayingStrategy(BotPlayingStrategy):
    def make_move(self, board: Board, me: Player) -> Move:
        return Move(me, _empty_cells(board)[0])          # a bot returns the REAL cell


class MediumBotPlayingStrategy(BotPlayingStrategy):
    """Win if you can, block if you must, otherwise the first empty cell."""

    def make_move(self, board: Board, me: Player) -> Move:
        empties = _empty_cells(board)
        for cell in empties:
            if _completes_line(board, cell, me.symbol):
                return Move(me, cell)
        opponents = {c.player.symbol for row in board.grid for c in row
                     if c.player is not None and c.player.symbol != me.symbol}
        for cell in empties:
            if any(_completes_line(board, cell, s) for s in opponents):
                return Move(me, cell)
        return Move(me, empties[0])


class HardBotPlayingStrategy(BotPlayingStrategy):
    def make_move(self, board: Board, me: Player) -> Move:
        raise NotImplementedError("minimax needs a depth limit on boards larger than 3 x 3")


class BotPlayingStrategyFactory:
    _BY_LEVEL: dict[BotDifficultyLevel, type[BotPlayingStrategy]] = {
        BotDifficultyLevel.EASY: EasyBotPlayingStrategy,
        BotDifficultyLevel.MEDIUM: MediumBotPlayingStrategy,
        BotDifficultyLevel.HARD: HardBotPlayingStrategy,
    }

    @staticmethod
    def for_level(level: BotDifficultyLevel) -> BotPlayingStrategy:
        return BotPlayingStrategyFactory._BY_LEVEL[level]()      # the only place difficulty maps to behaviour


class Bot(Player):
    def __init__(self, name: str, symbol: Symbol, level: BotDifficultyLevel) -> None:
        super().__init__(name, symbol, PlayerType.BOT)
        self.level = level
        self._strategy = BotPlayingStrategyFactory.for_level(level)

    def make_move(self, board: Board) -> Move:
        return self._strategy.make_move(board, self)
```

### Running it

Two scenarios: the medium bot blocking the main diagonal, and the stale-counter trap. In the second, Alice wins on row 0, the winning move is undone, and the same move is replayed. If `handle_undo` had forgotten to decrement the row counter, row 0 would hold a count of 4 on the replay, and the equality test `== N` would silently miss the win.

```python
def fresh_strategies() -> list[WinningStrategy]:
    return [RowCountStrategy(), ColumnCountStrategy(), DiagonalCountStrategy()]


# 1) Medium bot blocks the diagonal
alice = ScriptedPlayer("Alice", Symbol("X"), [(0, 0), (1, 1)])
bot = Bot("Bot", Symbol("O"), BotDifficultyLevel.MEDIUM)
game = GameController().start_game(3, [alice, bot], fresh_strategies())
for _ in range(4):
    game.make_move()
print(game.board.render())

# 2) undo a winning move, then replay it: a stale counter would miss the second win
alice = ScriptedPlayer("Alice", Symbol("X"), [(0, 0), (0, 1), (0, 2), (0, 2)])
bob = ScriptedPlayer("Bob", Symbol("O"), [(1, 0), (1, 1)])
game = GameController().start_game(3, [alice, bob], fresh_strategies())
for _ in range(5):
    game.make_move()
print(game.state.name, game.winner.name)
game.undo()
print(game.state.name, game.winner, game.next_player_index)
game.make_move()
print(game.state.name, game.winner.name)
```

```text
X O -
- X -
- - O
ENDED Alice
IN_PROGRESS None 0
ENDED Alice
```

### Tests, including a differential test

Example-based tests pin the behaviours above. The last test is the more interesting one: a **differential test** runs two games in lockstep, one with the counting strategies and one with the simple scanning strategies from the previous lesson, applies the same random moves and undos to both, and asserts that their states always agree. The scanning version is slow but obviously correct, so it acts as the oracle for the clever one. This pattern is worth using whenever you optimise something.

```python
import random

import pytest


def make(strategies, level=None):
    players = [ScriptedPlayer("A", Symbol("X"), []), ScriptedPlayer("B", Symbol("O"), [])]
    return GameController().start_game(3, players, strategies)


class QueuedPlayer(Player):
    """Receives its next move from the test harness."""

    def __init__(self, name: str, symbol: Symbol) -> None:
        super().__init__(name, symbol)
        self.next: tuple[int, int] = (0, 0)

    def make_move(self, board: Board) -> Move:
        return Move(self, Cell(*self.next))


def test_undo_on_empty_game_raises() -> None:
    with pytest.raises(EmptyMovesError):
        make(fresh_strategies()).undo()


def test_undo_restores_cell_and_turn() -> None:
    game = GameController().start_game(
        3, [ScriptedPlayer("A", Symbol("X"), [(0, 0)]), ScriptedPlayer("B", Symbol("O"), [(1, 1)])],
        fresh_strategies())
    game.make_move()
    game.make_move()
    game.undo()
    assert game.next_player_index == 1 and len(game.moves) == 1
    assert game.board.grid[1][1].state is CellState.EMPTY and game.board.grid[1][1].player is None
    game.undo()
    assert game.next_player_index == 0 and not game.moves


def test_undone_winning_move_can_win_again() -> None:
    alice = ScriptedPlayer("A", Symbol("X"), [(0, 0), (0, 1), (0, 2), (0, 2)])
    bob = ScriptedPlayer("B", Symbol("O"), [(1, 0), (1, 1)])
    game = GameController().start_game(3, [alice, bob], fresh_strategies())
    for _ in range(5):
        game.make_move()
    assert game.state is GameState.ENDED
    game.undo()
    assert game.state is GameState.IN_PROGRESS and game.winner is None
    game.make_move()
    assert game.state is GameState.ENDED and game.winner is alice


def test_medium_bot_wins_when_it_can_and_blocks_otherwise() -> None:
    bot = Bot("Bot", Symbol("O"), BotDifficultyLevel.MEDIUM)
    game = GameController().start_game(3, [ScriptedPlayer("A", Symbol("X"), [(0, 0), (1, 1)]), bot],
                                       fresh_strategies())
    for _ in range(4):
        game.make_move()
    assert game.board.grid[2][2].player is bot             # blocked the main diagonal


def test_counters_agree_with_rescan_under_random_play_and_undo() -> None:
    rng = random.Random(2024)
    scanning = lambda: [RowWinningStrategy(), ColumnWinningStrategy(), DiagonalWinningStrategy()]
    for _ in range(150):
        games = []
        for strategies in (fresh_strategies(), scanning()):
            players = [QueuedPlayer("A", Symbol("X")), QueuedPlayer("B", Symbol("O"))]
            games.append(GameController().start_game(3, players, strategies))
        for _ in range(30):
            if games[0].moves and rng.random() < 0.25:
                for g in games:
                    g.undo()
            elif games[0].state is GameState.IN_PROGRESS:
                cell = (rng.randrange(3), rng.randrange(3))
                outcomes = []
                for g in games:
                    g.players[g.next_player_index].next = cell
                    try:
                        g.make_move()
                        outcomes.append("ok")
                    except InvalidMoveError:
                        outcomes.append("invalid")
                assert outcomes[0] == outcomes[1]
            seen = [(g.state, g.winner.name if g.winner else None) for g in games]
            assert seen[0] == seen[1]
```

I ran this suite and all five tests passed, including 150 randomised games with undo.

### Patterns recap

Builder validates the configuration and constructs `Game`. Strategy appears twice, for winning and for bot play. Factory maps a difficulty level to a strategy. Inheritance is used where it is true (a `Bot` is a `Player`), and composition where it is not (a `Game` has a `Board`). If an interviewer asks you to name the patterns, point at these four decisions and say which requirement drove each.

## Practical Backend Scenario

An agent platform needs a per-tenant budget guard that decides after every model call whether any limit (tokens per minute, spend per day) is exceeded, and must refund a call when it is cancelled. A naive guard rescans the window per request. The TicTacToe solution transfers directly: running counters per (tenant, limit) make the check O(1), a `handle_undo` refunds a cancelled call, and a differential test compares the fast guard with a slow rescan on random calls and cancellations. The same traps appear: counters shared between tenants, and a short-circuiting `any` that stops updating later guards.

## Practice Loop

1. Replace the scanning strategies from lesson 20 with the three counting strategies. Run the demo and confirm a row win, a column win and both diagonals on a 3 x 3 and a 4 x 4 board with three players.
2. Implement `Game.undo`, then deliberately remove the `handle_undo` decrement from one strategy and confirm that the "undone winning move can win again" test fails. Restore it.
3. Change `_has_winner` back to `any(generator)` and find a scenario with two stateful strategies where it produces a wrong answer. Explain it in two sentences.
4. Implement the medium bot and test it against a scripted opponent: it takes an immediate win, blocks an immediate loss, and otherwise plays the first empty cell.
5. Run the differential test with a different seed and with 4 x 4 boards (three players). Fix whatever it finds.
6. Time-box the whole lesson at 90 minutes and speak your reasoning for the complexity ladder aloud.

## Evidence of Understanding

- I can walk the complexity ladder from O(N^3) to O(1) and explain why each step is valid.
- I can explain why counters must be keyed by symbol, and why a plain dict fails on first use.
- I can state why the two diagonals use independent `if` statements.
- I can list the four duties of undo and say what goes wrong if each is forgotten.
- I can explain why stateful strategies must not be shared across games and must all see every move.
- I can describe the identity gap and how passing the player to the bot strategy closes it.
- I can say what a differential test is and why the slow implementation is the oracle.

## Interview Questions to Rehearse

### Q: How do you make the win check O(1), and what does it cost?

A counter per row, column and diagonal for each symbol. A move increments at most four counters and compares with N, which is constant time, at the cost of 2N + 2 counters per symbol and keeping them correct: per symbol, to avoid false wins, and reversible if undo exists.

### Q: How would you implement undo, and what are the alternatives?

Keep a stack of moves. Undo pops one, clears the real cell, restores the turn index, rolls back every derived structure, and resets the state. The alternative is snapshotting the whole state per move: simpler, but O(N^2) memory per move. I chose inverse operations for O(1) cost; the price is a `handle_undo` on each strategy, which I verify with a differential test.

### Q: Why is `any()` over stateful strategies a bug?

`any` over a generator short-circuits at the first `True`, so later strategies never see the move and their counters stop tracking the board. It usually does not matter because the game ends, but with undo the game continues and results go wrong. Compute all results first, then reduce them.

### Q: Why does the bot strategy receive the player as an argument?

Because the board does not know whose turn it is, and a blocking strategy needs to know which symbols are "mine" and which are the opponent's. A strategy interface that takes only the board is one level too thin. Passing `me` also lets one strategy class serve any player, so no per-player subclass is needed.

### Q: How do you test an optimisation like this one?

Differentially: run the fast implementation and a simple, obviously correct one on identical randomised inputs (random moves and undos) and assert agreement at every step, plus example tests for named behaviours. Randomness is seeded so failures reproduce.

## Common Pitfalls

- Sharing stateful strategy objects between games, so counters mix.
- One counter per line instead of per (line, symbol), giving false wins on mixed lines.
- Forgetting to decrement counters in undo, so replayed moves miss wins.
- Using `any(generator)` with stateful strategies, so later ones skip updates.
- Undoing without resetting `state` and `winner`, so a resumed game stays finished.
- Clearing the detached cell in a human's `Move` instead of the real board cell.
- Giving the bot strategy only the board, so it cannot tell its marks from the opponent's.
- Shipping minimax with no depth limit, which freezes on a 5 x 5 board.

## Suggested Extension

Implement redo: keep a second stack of undone moves, clear it whenever a new move is played, and re-apply a move by replaying it through the same validation and strategy updates. Then extend the differential test to include random redo operations, and decide whether `HardBotPlayingStrategy` should become a depth-limited minimax with alpha-beta pruning, justifying your depth limit for a 4 x 4 board.
