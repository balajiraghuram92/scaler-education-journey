package com.example.boardgamecreation;

public class ChessBoardGame extends BoardGame {
    public ChessBoardGame(String boardGameName) {
        super(boardGameName);
    }

    @Override
    public void playGame() {
        //Implement logic for playing Chess
        System.out.println("Playing Chess");
    }

    @Override
    public GameType gameType() {
        return GameType.CHESS;
    }
}
