from typing import Dict
from models.board import Board
from models.move import Move
from models.symbol import Symbol
from strategies.winning_strategy import WinningStrategy

class WinningStrategyImpl(WinningStrategy):

    def __init__(self):
        """Create row_maps and col_maps (row or column index -> {symbol: count}) and left_diagonal_map and right_diagonal_map ({symbol: count})."""
        raise NotImplementedError('TODO: implement __init__')

    def check_winner(self, board: Board, move: Move) -> bool:
        """Increment the counters of move.player.symbol for the move's row, column, left diagonal (row == col) and right diagonal (row + col == dimension - 1). Return True when any of those counts equals board.dimension."""
        raise NotImplementedError('TODO: implement check_winner')
