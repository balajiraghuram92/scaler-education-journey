from typing import Dict
from models.board import Board
from models.move import Move
from models.symbol import Symbol
from strategies.winning_strategy import WinningStrategy

class WinningStrategyImpl(WinningStrategy):
    def __init__(self):
        self.row_maps: Dict[int, Dict[Symbol, int]] = {}
        self.col_maps: Dict[int, Dict[Symbol, int]] = {}
        self.left_diagonal_map: Dict[Symbol, int] = {}
        self.right_diagonal_map: Dict[Symbol, int] = {}

    def check_winner(self, board: Board, move: Move) -> bool:
        row = move.cell.row
        col = move.cell.col
        symbol = move.player.symbol

        # Update row map
        if row not in self.row_maps:
            self.row_maps[row] = {}
        self.row_maps[row][symbol] = self.row_maps[row].get(symbol, 0) + 1

        # Update col map
        if col not in self.col_maps:
            self.col_maps[col] = {}
        self.col_maps[col][symbol] = self.col_maps[col].get(symbol, 0) + 1

        # Update left diagonal map
        if row == col:
            self.left_diagonal_map[symbol] = self.left_diagonal_map.get(symbol, 0) + 1

        # Update right diagonal map
        if row + col == board.dimension - 1:
            self.right_diagonal_map[symbol] = self.right_diagonal_map.get(symbol, 0) + 1

        # Check conditions
        if row == col and self.left_diagonal_map.get(symbol, 0) == board.dimension:
            return True
        if row + col == board.dimension - 1 and self.right_diagonal_map.get(symbol, 0) == board.dimension:
            return True
        if self.row_maps[row].get(symbol, 0) == board.dimension:
            return True
        if self.col_maps[col].get(symbol, 0) == board.dimension:
            return True
            
        return False
