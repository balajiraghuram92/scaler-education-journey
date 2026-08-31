package com.example.tttundo.strategies;

import com.example.tttundo.models.Board;
import com.example.tttundo.models.Move;
import com.example.tttundo.models.Symbol;

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
//   - undoMove(...) is the inverse: decrement the same counters that checkWinner incremented
//     for that move, so the strategy's state stays consistent after Game.undo().
public class WinningStrategyImpl implements WinningStrategy {
    private Map<Integer, Map<Symbol, Integer>> rowMaps = new HashMap<>();
    private Map<Integer, Map<Symbol, Integer>> colMaps = new HashMap<>();
    private Map<Symbol, Integer> leftDiagonalMap = new HashMap<>();
    private Map<Symbol, Integer> rightDiagonalMap = new HashMap<>();

    @Override
    public boolean checkWinner(Board board, Move move) {
        return false;
    }

    public void undoMove(Move move, int dimension) {

    }
}
