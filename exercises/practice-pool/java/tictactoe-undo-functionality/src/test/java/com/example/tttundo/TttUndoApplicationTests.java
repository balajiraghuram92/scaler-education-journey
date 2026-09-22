package com.example.tttundo;

import com.example.tttundo.controllers.GameController;
import com.example.tttundo.exceptions.EmptyMovesException;
import com.example.tttundo.models.*;
import com.example.tttundo.strategies.WinningStrategy;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import static org.junit.jupiter.api.Assertions.*;

import java.util.ArrayList;
import java.util.List;

@SpringBootTest
class TttUndoApplicationTests {
    private Game game;
    private GameController gameController;
    private List<Player> players;
    private WinningStrategy winningStrategy;
    private Board board;

    @BeforeEach
    public void initializeGame() throws Exception {
        gameController = new GameController();
        int dimension = 3;
        players = new ArrayList<>();
        players.add(new Player("Player1", new Symbol('X')));
        players.add(new Player("Player2", new Symbol('O')));
        game = gameController.startGame(dimension, players);
    }

    @Test
    public void testGameWinningCase() {
        Player player1 = players.get(0);
        Player player2 = players.get(1);
        Board board = game.getBoard();
        winningStrategy = game.getWinningStrategy();

        makeMove(board, player1, 0, 0); //P1 -> 0,0
        makeMove(board, player2, 1, 1 ); //P2 -> 1,1
        makeMove(board, player1, 0, 1); //P1 -> 0,1
        makeMove(board, player2, 1, 2); //P2 -> 1,2

        //Winning move
        board.getBoard().get(0).get(2).setPlayer(player1);
        board.getBoard().get(0).get(2).setCellState(CellState.FILLED);

        assertTrue(winningStrategy.checkWinner(board, new Move(player1, new Cell(0, 2))),
                "Player 1 should be the winner");
    }

    @Test
    public void testUndoFunctionality1() throws EmptyMovesException {
        board = game.getBoard();
        Player player1 = players.get(0);
        List<Move> moves = game.getMoves();

        makeMove(board, player1,0, 0);
        gameController.undo(game);

        assertEquals(board.getBoard().get(0).get(0).getCellState(), CellState.EMPTY);
    }

    @Test
    public void testUndoFunctionality2() throws EmptyMovesException {
        board = game.getBoard();
        Player player1 = players.get(0);
        Player player2 = players.get(1);
        List<Move> moves = game.getMoves();

        makeMove(board, player1, 0, 2);
        makeMove(board, player2, 1, 1);
        makeMove(board, player1, 2, 0);
        makeMove(board, player2, 2, 2);

        gameController.undo(game);
        gameController.undo(game);
        gameController.undo(game);

        boolean flag = board.getBoard().get(1).get(1).getCellState().equals(CellState.EMPTY) &&
                board.getBoard().get(2).get(0).getCellState().equals(CellState.EMPTY) &&
                board.getBoard().get(2).get(2).getCellState().equals(CellState.EMPTY) &&
                board.getBoard().get(0).get(2).getCellState().equals(CellState.FILLED);

        assertTrue(flag);
    }

    @Test
    public void testUndoFunctionality3() {
        board = game.getBoard();
        Player player1 = players.get(0);
        Player player2 = players.get(1);
        List<Move> moves = game.getMoves();

        Throwable exception = assertThrows(EmptyMovesException.class, () -> gameController.undo(game));
        assertEquals("Undo operation can't be performed as the moves list is empty",
                exception.getMessage());
    }

    private void makeMove(Board board, Player player, int row, int col) {
        board.getBoard().get(row).get(col).setPlayer(player);
        board.getBoard().get(row).get(col).setCellState(CellState.FILLED);
        Move move = new Move(player, new Cell(row, col));
        game.getMoves().add(move);
        game.getWinningStrategy().checkWinner(board, move);
    }
}
