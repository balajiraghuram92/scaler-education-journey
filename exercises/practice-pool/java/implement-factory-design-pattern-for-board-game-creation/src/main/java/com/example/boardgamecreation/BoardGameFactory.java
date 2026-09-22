package com.example.boardgamecreation;

public class BoardGameFactory {
    public static BoardGame createGame(GameType gameType, String boardGameName) {
        return switch (gameType) {
            case TIC_TAC_TOE -> new TicTacToeBoardGame(boardGameName);
            case CHESS -> new ChessBoardGame(boardGameName);
            case SNAKE_LADDER -> new SnakeLadderBoardGame(boardGameName);
            default -> throw new IllegalArgumentException("Unsupported game type : " + gameType);
        };
    }
}
