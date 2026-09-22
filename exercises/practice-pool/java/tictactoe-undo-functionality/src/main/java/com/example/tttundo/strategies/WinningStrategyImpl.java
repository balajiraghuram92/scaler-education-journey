package com.example.tttundo.strategies;

import com.example.tttundo.models.Board;
import com.example.tttundo.models.Move;
import com.example.tttundo.models.Symbol;

import java.util.HashMap;
import java.util.Map;

public class WinningStrategyImpl implements WinningStrategy {
    private Map<Integer, Map<Symbol, Integer>> rowMaps = new HashMap<>();
    private Map<Integer, Map<Symbol, Integer>> colMaps = new HashMap<>();
    private Map<Symbol, Integer> leftDiagonalMap = new HashMap<>();
    private Map<Symbol, Integer> rightDiagonalMap = new HashMap<>();

    @Override
    public boolean checkWinner(Board board, Move move) {
        int row = move.getCell().getRow();
        int col = move.getCell().getCol();
        Symbol symbol = move.getPlayer().getSymbol();

        //Update the Row Map
        if (!rowMaps.containsKey(row)) {
            rowMaps.put(row, new HashMap<Symbol, Integer>());
        }
        Map<Symbol, Integer> currentRowMap = rowMaps.get(row);

        if (currentRowMap.containsKey(symbol)) {
            currentRowMap.put(symbol,
                    currentRowMap.get(symbol) + 1);
        } else {
            currentRowMap.put(symbol, 1);
        }

        //Update the Col Map
        if (!colMaps.containsKey(col)) {
            colMaps.put(col, new HashMap<Symbol, Integer>());
        }

        Map<Symbol, Integer> currentColMap = colMaps.get(col);

        if (currentColMap.containsKey(symbol)) {
            currentColMap.put(symbol,
                    currentColMap.get(symbol) + 1);
        } else {
            currentColMap.put(symbol, 1);
        }

        if (row == col) {
            //Cell is present on left diagonal.
            if (leftDiagonalMap.containsKey(symbol)) {
                leftDiagonalMap.put(symbol,
                        leftDiagonalMap.get(symbol) + 1);
            } else {
                leftDiagonalMap.put(symbol, 1);
            }
        }

        if (row + col == board.getDimension() - 1) {
            //Cell is present on right diagonal.
            if (rightDiagonalMap.containsKey(symbol)) {
                rightDiagonalMap.put(symbol,
                        rightDiagonalMap.get(symbol) + 1);
            } else {
                rightDiagonalMap.put(symbol, 1);
            }
        }

        if (row == col && leftDiagonalMap.get(symbol) == board.getDimension()) {
            return true;
        }

        if (row + col == board.getDimension() - 1 &&
                rightDiagonalMap.get(symbol) == board.getDimension()) {
            return true;
        }

        return currentRowMap.get(symbol) == board.getDimension() ||
                currentColMap.get(symbol) == board.getDimension();
    }

    public void undoMove(Move move, int dimension) {
        int row = move.getCell().getRow();
        int col = move.getCell().getCol();
        Symbol symbol = move.getPlayer().getSymbol();

        rowMaps.get(row).put(symbol, rowMaps.get(row).get(symbol) - 1);
        colMaps.get(col).put(symbol, colMaps.get(col).get(symbol) - 1);
        if (row == col) {
            leftDiagonalMap.put(symbol, leftDiagonalMap.get(symbol) - 1);
        } if (row + col == dimension - 1) {
            rightDiagonalMap.put(symbol, rightDiagonalMap.get(symbol) - 1);
        }
    }
}
