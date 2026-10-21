from abc import ABC, abstractmethod
from game_type import GameType

class BoardGame(ABC):

    def __init__(self, board_game_name: str):
        """Store board_game_name."""
        raise NotImplementedError('TODO: implement __init__')

    def get_board_game_name(self) -> str:
        """Return the stored name."""
        raise NotImplementedError('TODO: implement get_board_game_name')

    @abstractmethod
    def play_game(self) -> None:
        pass

    @abstractmethod
    def game_type(self) -> GameType:
        pass
