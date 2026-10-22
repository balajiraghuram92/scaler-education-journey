from models.cell import Cell
from models.player import Player

class Move:
    def __init__(self, player: Player, cell: Cell):
        self.player = player
        self.cell = cell
