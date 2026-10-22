from typing import Optional
from models.enums import CellState
from models.player import Player

class Cell:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        self.cell_state = CellState.EMPTY
        self.player: Optional[Player] = None
