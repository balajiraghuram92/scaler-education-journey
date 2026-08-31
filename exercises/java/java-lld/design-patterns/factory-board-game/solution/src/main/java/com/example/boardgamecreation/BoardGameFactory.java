package com.example.boardgamecreation;

public class BoardGameFactory {
    public static BoardGame createGame(GameType gameType, String boardGameName) {
        switch (gameType) {
            case TIC_TAC_TOE:
                return new TicTacToeBoardGame(boardGameName);
            case CHESS:
                return new ChessBoardGame(boardGameName);
            case SNAKE_LADDER:
                return new SnakeLadderBoardGame(boardGameName);
            default:
                throw new IllegalArgumentException("Unsupported game type : " + gameType);
        }
    }
}
