package com.example.boardgamecreation;

public class SnakeLadderBoardGame extends BoardGame {

    public SnakeLadderBoardGame(String boardGameName) {
        super(boardGameName);
    }

    @Override
    public void playGame() {
        //Implement logic for playing Snake & Ladder
        System.out.println("Playing Snake & Ladder");
    }

    @Override
    public GameType gameType() {
        return GameType.SNAKE_LADDER;
    }
}
