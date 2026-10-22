from typing import List, Optional
from models.board import Board
from models.enums import GameState
from models.move import Move
from models.player import Player

class Game:
    def __init__(self, dimension: int, players: List[Player]):
        self.board = Board(dimension)
        self.players = players
        self.next_player_move_index = 0
        self.moves: List[Move] = []
        self.game_state = GameState.IN_PROGRESS
        self.winner: Optional[Player] = None
