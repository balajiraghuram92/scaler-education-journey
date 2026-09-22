package com.example.boardgamecreation;

public abstract class BoardGame {
    private String boardGameName;

    public BoardGame(String boardGameName) {
        this.boardGameName = boardGameName;
    }

    public String getBoardGameName() {
        return boardGameName;
    }

    public abstract void playGame();

    public abstract GameType gameType();
}
