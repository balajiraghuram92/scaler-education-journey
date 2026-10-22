from abc import ABC, abstractmethod
from models.board import Board
from models.move import Move

class WinningStrategy(ABC):
    @abstractmethod
    def check_winner(self, board: Board, move: Move) -> bool:
        pass
