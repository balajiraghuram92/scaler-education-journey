import random

from tictactoe.game import (
    Game, GameController, GameState, InvalidMoveError, Player, WinningStrategy,
)


class TooManyInvalidMovesError(Exception):
    """A player exceeded the allowed number of consecutive rejected moves."""


class SeededBuilder(Game.Builder):
    """FR-9: random first player, made deterministic in tests by injecting an RNG."""

    def __init__(self, rng: random.Random) -> None:
        super().__init__()
        self._rng = rng

    def build(self) -> Game:
        game = super().build()                       # keep every validation rule
        k = self._rng.randrange(len(game.players))
        game.players = game.players[k:] + game.players[:k]   # rotate: turn order is preserved
        return game


class RetryingController(GameController):
    def start_game_seeded(self, dimension: int, players: list[Player],
                          strategies: list[WinningStrategy], rng: random.Random) -> Game:
        builder = SeededBuilder(rng).set_dimension(dimension)
        for p in players:
            builder.add_player(p)
        for s in strategies:
            builder.add_winning_strategy(s)
        return builder.build()

    def play(self, game: Game, max_invalid_moves: int = 3) -> Game:
        invalid_in_a_row = 0
        while game.state is GameState.IN_PROGRESS:
            try:
                game.make_move()
                invalid_in_a_row = 0
            except InvalidMoveError:
                invalid_in_a_row += 1                # same player is asked again
                if invalid_in_a_row > max_invalid_moves:
                    raise TooManyInvalidMovesError(
                        f"{game.players[game.next_player_index].name} made {invalid_in_a_row} invalid moves"
                    ) from None
        return game
