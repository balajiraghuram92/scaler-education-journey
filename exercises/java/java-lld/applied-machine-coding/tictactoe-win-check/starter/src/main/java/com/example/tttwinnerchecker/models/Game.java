package com.example.tttwinnerchecker.models;

import com.example.tttwinnerchecker.exceptions.GameInvalidationException;
import com.example.tttwinnerchecker.exceptions.InvalidMoveException;
import com.example.tttwinnerchecker.strategies.WinningStrategy;
import com.example.tttwinnerchecker.strategies.WinningStrategyImpl;

import java.util.ArrayList;
import java.util.List;

public class Game {
    private Board board;
    private List<Player> players;
    private GameState gameState;
    private Player winner;
    private int nextPlayerMoveIndex;
    private List<Move> moves;

    private WinningStrategy winningStrategy;

    Game(int dimension, List<Player> players) {
        this.board = new Board(dimension);
        this.players = players;
        this.nextPlayerMoveIndex = 0;
        this.moves = new ArrayList<>();
        this.gameState = GameState.IN_PROGRESS;
        this.winningStrategy = new WinningStrategyImpl();
    }

    public static Builder getBuilder() {
        return new Builder();
    }

    public static class Builder {
        private int dimension;
        private List<Player> players;

        public Builder setDimension(int dimension) {
            this.dimension = dimension;
            return this;
        }

        public Builder setPlayers(List<Player> players) {
            this.players = players;
            return this;
        }

        private boolean validate() {
            return true;
        }

        public Game build() throws Exception {
            //validate.
            if (!validate()) {
                throw new GameInvalidationException("Invalid game");
            }

            //create the Game object.
            return new Game(dimension, players);
        }

    }

    public Board getBoard() {
        return board;
    }

    public void setBoard(Board board) {
        this.board = board;
    }

    public List<Player> getPlayers() {
        return players;
    }

    public void setPlayers(List<Player> players) {
        this.players = players;
    }

    public GameState getGameState() {
        return gameState;
    }

    public void setGameState(GameState gameState) {
        this.gameState = gameState;
    }

    public Player getWinner() {
        return winner;
    }

    public void setWinner(Player winner) {
        this.winner = winner;
    }

    public int getNextPlayerMoveIndex() {
        return nextPlayerMoveIndex;
    }

    public void setNextPlayerMoveIndex(int nextPlayerMoveIndex) {
        this.nextPlayerMoveIndex = nextPlayerMoveIndex;
    }

    public List<Move> getMoves() {
        return moves;
    }

    public void setMoves(List<Move> moves) {
        this.moves = moves;
    }

    public WinningStrategy getWinningStrategy() {
        return winningStrategy;
    }

    public void setWinningStrategy(WinningStrategy winningStrategy) {
        this.winningStrategy = winningStrategy;
    }


    public void displayBoard(Board board) {
        board.displayBoard();
    }

    private boolean checkWinner(Board board, Move move) {
        return winningStrategy.checkWinner(board, move);
    }

    // TODO: return true only when the move's row and col are within [0, dimension) AND
    // the target cell is currently CellState.EMPTY.
    public boolean validateMove(Move move) {
        return false;
    }

    // TODO: make the current player's move (get their Move via currentPlayer.makeMove(board),
    // validate it with validateMove(...), throw InvalidMoveException if invalid, otherwise
    // apply it to the board, append it to moves, advance nextPlayerMoveIndex (wrapping with
    // % players.size()), and update gameState/winner if checkWinner(...) returns true or the
    // board is full.
    public void makeMove() throws InvalidMoveException {

    }
}
