package com.example.tttundo.models;

import com.example.tttundo.exceptions.EmptyMovesException;
import com.example.tttundo.exceptions.GameInvalidationException;
import com.example.tttundo.exceptions.InvalidMoveException;
import com.example.tttundo.strategies.WinningStrategy;
import com.example.tttundo.strategies.WinningStrategyImpl;

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

    public WinningStrategy getWinningStrategy() {
        return winningStrategy;
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

    public void displayBoard(Board board) {
        board.displayBoard();
    }

    private boolean checkWinner(Board board, Move move) {
        return winningStrategy.checkWinner(board, move);
    }

    private boolean validateMove(Move move) {
        int row = move.getCell().getRow();
        int col = move.getCell().getCol();

        return row < board.getDimension() && row >= 0 && col < getBoard().getDimension() && col >= 0 &&
                board.getBoard().get(row).get(col).getCellState().equals(CellState.EMPTY);
    }

    // TODO: make the current player's move (get their Move via currentPlayer.makeMove(board),
    // validate it with validateMove(...), throw InvalidMoveException if invalid, otherwise
    // apply it to the board, append it to moves, advance nextPlayerMoveIndex (wrapping with
    // % players.size()), and update gameState/winner if checkWinner(...) returns true or the
    // board is full.
    public void makeMove() throws InvalidMoveException {

    }

    // TODO: undo the last move — pop it off moves, ask board to clear that cell
    // (board.undoMove(...)), roll nextPlayerMoveIndex back by one (wrapping with
    // players.size()), and tell the WinningStrategyImpl to undo its counters for that move.
    // If there is no move to undo, throw EmptyMovesException("Undo operation can't be
    // performed as the moves list is empty").
    public void undo() throws EmptyMovesException {

    }
}
