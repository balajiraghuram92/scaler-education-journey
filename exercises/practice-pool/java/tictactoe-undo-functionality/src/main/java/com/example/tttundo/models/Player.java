package com.example.tttundo.models;

import java.util.Scanner;

public class Player {
    private String name;
    private Symbol symbol;

    public Player(String name, Symbol symbol) {
        this.name = name;
        this.symbol = symbol;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Symbol getSymbol() {
        return symbol;
    }

    public void setSymbol(Symbol symbol) {
        this.symbol = symbol;
    }

    public Move makeMove(Board board) {
        Scanner scanner = new Scanner(System.in);

        //Ask the Player to provide the index to make a move.
        System.out.println("Please tell the row index to make a move");
        int rowNumber = scanner.nextInt();

        System.out.println("Please tell the col index to make a move");
        int colNumber = scanner.nextInt();

        return new Move(this, new Cell(rowNumber, colNumber));
    }
}
