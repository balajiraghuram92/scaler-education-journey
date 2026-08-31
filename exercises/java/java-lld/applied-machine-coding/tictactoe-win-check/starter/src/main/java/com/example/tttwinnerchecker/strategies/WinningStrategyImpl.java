package com.example.tttwinnerchecker.strategies;

import com.example.tttwinnerchecker.models.Board;
import com.example.tttwinnerchecker.models.Move;
import com.example.tttwinnerchecker.models.Symbol;

import java.util.HashMap;
import java.util.Map;

// TODO: implement WinningStrategy in O(1) per move using running counters instead of
// re-scanning the board:
//   - rowMaps/colMaps: for each row/col, count how many cells each Symbol occupies.
//   - leftDiagonalMap/rightDiagonalMap: same counters for the two diagonals (a cell is on
//     the left diagonal when row == col, on the right diagonal when row + col == dimension - 1).
//   - checkWinner(...) increments the relevant counters for the move's row, col, and
//     (if applicable) diagonals, then returns true if any counter for this move's Symbol
//     has reached board.getDimension().
public class WinningStrategyImpl implements WinningStrategy {
    private Map<Integer, Map<Symbol, Integer>> rowMaps = new HashMap<>();
    private Map<Integer, Map<Symbol, Integer>> colMaps = new HashMap<>();
    private Map<Symbol, Integer> leftDiagonalMap = new HashMap<>();
    private Map<Symbol, Integer> rightDiagonalMap = new HashMap<>();

    @Override
    public boolean checkWinner(Board board, Move move) {
        return false;
    }
}
