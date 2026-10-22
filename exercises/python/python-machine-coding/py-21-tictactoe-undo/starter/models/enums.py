from enum import Enum

class CellState(Enum):
    EMPTY = 1
    FILLED = 2

class GameState(Enum):
    IN_PROGRESS = 1
    ENDED = 2
    DRAW = 3
