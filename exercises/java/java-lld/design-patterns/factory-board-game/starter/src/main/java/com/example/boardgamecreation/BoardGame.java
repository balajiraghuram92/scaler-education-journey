package com.example.boardgamecreation;

// TODO: add a private String field for the board game's name, set it via the
// constructor, and expose it through getBoardGameName(). playGame() and gameType()
// stay abstract — each concrete game implements its own.
public abstract class BoardGame {
    private String boardGameName;

    public BoardGame(String boardGameName) {
        this.boardGameName = boardGameName;
    }

    public String getBoardGameName() {
        return null;
    }

    public abstract void playGame();

    public abstract GameType gameType();
}
