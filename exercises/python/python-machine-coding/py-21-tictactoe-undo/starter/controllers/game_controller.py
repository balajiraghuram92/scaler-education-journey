from typing import List
from models.enums import GameState
from models.game import Game
from models.player import Player
from services.game_service import GameService

class GameController:
    def __init__(self, game_service: GameService):
        self.game_service = game_service

    def start_game(self, dimension: int, players: List[Player]) -> Game:
        return self.game_service.start_game(dimension, players)

    def make_move(self, game: Game, row: int, col: int) -> None:
        self.game_service.make_move(game, row, col)

    def undo(self, game: Game) -> None:
        self.game_service.undo(game)

    def get_game_state(self, game: Game) -> GameState:
        return game.game_state

    def get_winner(self, game: Game) -> Player:
        return game.winner
