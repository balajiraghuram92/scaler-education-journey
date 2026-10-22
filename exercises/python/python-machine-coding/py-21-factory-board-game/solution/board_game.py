from abc import ABC, abstractmethod
from game_type import GameType

class BoardGame(ABC):
    def __init__(self, board_game_name: str):
        self.board_game_name = board_game_name

    def get_board_game_name(self) -> str:
        return self.board_game_name

    @abstractmethod
    def play_game(self) -> None:
        pass
    
    @abstractmethod
    def game_type(self) -> GameType:
        pass
