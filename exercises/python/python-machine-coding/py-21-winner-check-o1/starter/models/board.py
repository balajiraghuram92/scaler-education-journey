from typing import List
from models.cell import Cell

class Board:
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.board: List[List[Cell]] = []
        for i in range(dimension):
            row = []
            for j in range(dimension):
                row.append(Cell(i, j))
            self.board.append(row)
