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

    public void makeMove() throws InvalidMoveException {
        Player currentPlayer = players.get(nextPlayerMoveIndex);

        System.out.println("It is " + currentPlayer.getName() + "'s move.");
        Move move = currentPlayer.makeMove(board);

        System.out.println(currentPlayer.getName() + " has made a move at Row: " + move.getCell().getRow() +
                ", col: " + move.getCell().getCol() + ".");

        //Validate the move before we apply the move on Board.
        if (!validateMove(move)) {
            System.out.println("Invalid move by player: " + currentPlayer.getName());
            throw new InvalidMoveException("Invalid move made by player: " + currentPlayer.getName());
        }

        int row = move.getCell().getRow();
        int col = move.getCell().getCol();
        Cell finalCellToMakeMove = board.getBoard().get(row).get(col);
        finalCellToMakeMove.setCellState(CellState.FILLED);
        finalCellToMakeMove.setPlayer(currentPlayer);

        Move finalMove = new Move(currentPlayer, finalCellToMakeMove);
        moves.add(finalMove);

        nextPlayerMoveIndex += 1;
        nextPlayerMoveIndex %= players.size();
        if (checkWinner(board, finalMove)) {
            gameState = GameState.ENDED;
            winner = currentPlayer;
        } else if (moves.size() == board.getDimension() * board.getDimension()) {
            gameState = GameState.DRAW;
        }
    }

    public void undo() throws EmptyMovesException {
        if (!moves.isEmpty()) {
            Move lastMove = moves.remove(moves.size() - 1);
            board.undoMove(lastMove);

            nextPlayerMoveIndex = (nextPlayerMoveIndex - 1 + players.size()) % players.size();
            ((WinningStrategyImpl) winningStrategy).undoMove(lastMove, board.getDimension());
        } else {
            throw new EmptyMovesException("Undo operation can't be performed as the moves list is empty");
        }
    }
}
