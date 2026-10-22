import random
from tictactoe.game import Game, GameController, GameState, InvalidMoveError, Player, WinningStrategy

class TooManyInvalidMovesError(Exception):
    """A player exceeded the allowed number of consecutive rejected moves."""

class SeededBuilder(Game.Builder):
    """FR-9: random first player, made deterministic in tests by injecting an RNG."""

    def __init__(self, rng: random.Random) -> None:
        """Call super().__init__() and keep the injected rng."""
        raise NotImplementedError('TODO: implement __init__')

    def build(self) -> Game:
        """Run the parent build() so every validation still applies, then rotate game.players left by rng.randrange(len(players)) so turn order is kept."""
        raise NotImplementedError('TODO: implement build')

class RetryingController(GameController):

    def start_game_seeded(self, dimension: int, players: list[Player], strategies: list[WinningStrategy], rng: random.Random) -> Game:
        """Like start_game, but build with a SeededBuilder(rng)."""
        raise NotImplementedError('TODO: implement start_game_seeded')

    def play(self, game: Game, max_invalid_moves: int=3) -> Game:
        """Call game.make_move() until the state leaves IN_PROGRESS and return the game. An InvalidMoveError re-asks the same player; the consecutive-invalid counter resets after any valid move. When it exceeds max_invalid_moves raise TooManyInvalidMovesError (use `from None`)."""
        raise NotImplementedError('TODO: implement play')
