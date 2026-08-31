package com.example.tttundo.models;

import java.util.ArrayList;
import java.util.List;

public class Board {
    private int dimension;
    private List<List<Cell>> board;

    public int getDimension() {
        return dimension;
    }

    public void setDimension(int dimension) {
        this.dimension = dimension;
    }

    public List<List<Cell>> getBoard() {
        return board;
    }

    public void setBoard(List<List<Cell>> board) {
        this.board = board;
    }

    public Board(int dimension) {
        //Initialize the board of size dimension * dimension
        this.dimension = dimension;
        board = new ArrayList<>(); // ROWS

        for (int i = 0; i < dimension; i++) {
            board.add(new ArrayList<>());

            for (int j = 0; j < dimension; j++) {
                board.get(i).add(new Cell(i, j));
            }
        }
    }

    public void displayBoard() {
        for (int i = 0; i < dimension; i++) {
            for (int j = 0; j < dimension; j++) {
                Cell cell = board.get(i).get(j);
                if (cell.getCellState().equals(CellState.EMPTY)) {
                    System.out.print("|  |");
                } else {
                    System.out.print("|" + cell.getPlayer().getSymbol().getSymbol() + "|");
                }
            }
            System.out.println();
        }
    }

    public void undoMove(Move move) {
        int removedRow = move.getCell().getRow();
        int removedCol = move.getCell().getCol();

        Cell cell = board.get(removedRow).get(removedCol);
        cell.setPlayer(null);
        cell.setCellState(CellState.EMPTY);
    }
}
