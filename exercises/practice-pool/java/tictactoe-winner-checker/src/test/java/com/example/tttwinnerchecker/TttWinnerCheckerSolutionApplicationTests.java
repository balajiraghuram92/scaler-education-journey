package com.example.tttwinnerchecker;

import com.example.tttwinnerchecker.exceptions.InvalidMoveException;
import com.example.tttwinnerchecker.models.*;
import com.example.tttwinnerchecker.controllers.GameController;
import com.example.tttwinnerchecker.strategies.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class TttWinnerCheckerSolutionApplicationTests {
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
    public void testGameWinningCase1() throws InvalidMoveException {
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
    public void testGameWinningCase2() throws InvalidMoveException {
        Player player1 = players.get(0);
        Player player2 = players.get(1);
        Board board = game.getBoard();
        winningStrategy = game.getWinningStrategy();

        makeMove(board, player1, 1, 1); //P1 -> 1,1
        makeMove(board, player2, 0, 0); //P2 -> 0,0
        makeMove(board, player1, 0, 2); //P1 -> 0,2
        makeMove(board, player2, 1, 0); //P2 -> 1,0

        //Winning move
        board.getBoard().get(2).get(0).setPlayer(player1);
        board.getBoard().get(2).get(0).setCellState(CellState.FILLED);
        board.displayBoard();

        assertTrue(winningStrategy.checkWinner(board, new Move(player1, new Cell(2, 0))),
                "Player 1 should be the winner");
    }

    @Test
    public void testGameWinningCase3() throws InvalidMoveException {
        Player player1 = players.get(0);
        Player player2 = players.get(1);
        Board board = game.getBoard();
        winningStrategy = game.getWinningStrategy();

        makeMove(board, player1, 1, 1); //P1 -> 1,1
        makeMove(board, player2, 0, 2); //P2 -> 0,2
        makeMove(board, player1, 0, 0); //P1 -> 0,0
        makeMove(board, player2, 1, 2); //P2 -> 1,2

        //Winning move
        board.getBoard().get(2).get(2).setPlayer(player1);
        board.getBoard().get(2).get(2).setCellState(CellState.FILLED);

        assertTrue(winningStrategy.checkWinner(board, new Move(player1, new Cell(2, 2))),
                "Player 1 should be the winner");
    }

    @Test
    public void testGameWinningCase4() throws InvalidMoveException {
        Player player1 = players.get(0);
        Player player2 = players.get(1);
        Board board = game.getBoard();
        winningStrategy = game.getWinningStrategy();

        makeMove(board, player1, 1, 1); //P1 -> 1,1
        makeMove(board, player2, 0, 2); //P2 -> 0,2
        makeMove(board, player1, 0, 0); //P1 -> 0,0
        makeMove(board, player2, 2, 2); //P2 -> 2,2
        makeMove(board, player1, 1, 2); //P1 -> 1,2
        makeMove(board, player2, 1, 0); //P2 -> 1,0
        makeMove(board, player1, 0, 1); //P2 -> 0,1
        makeMove(board, player2, 2, 1); //P2 -> 2,1
        makeMove(board, player1, 2, 0); // P1 -> 2,0

        assertTrue(isGameDraw(board), "Game should've been DRAWN");
    }

    @Test
    public void testInvalidMove() throws InvalidMoveException {
        Player player1 = players.get(0);
        Player player2 = players.get(1);
        Board board = game.getBoard();
        winningStrategy = game.getWinningStrategy();

        makeMove(board, player1, 0, 0); //P1 -> 0,0
        makeMove(board, player2, 1, 1 ); //P2 -> 1,1
        makeMove(board, player1, 0, 1); //P1 -> 0,1
        makeMove(board, player2, 1, 2); //P2 -> 1,2

        //Invalid Move.
        Throwable exception = assertThrows(InvalidMoveException.class, () -> makeMove(board, player1, 3, 0));
        assertEquals("Invalid move made by the Player", exception.getMessage());
    }


    private void makeMove(Board board, Player player, int row, int col) throws InvalidMoveException {
        Move move = new Move(player, new Cell(row, col));

        if (!game.validateMove(move)) {
            throw new InvalidMoveException("Invalid move made by the Player");
        }

        board.getBoard().get(row).get(col).setPlayer(player);
        board.getBoard().get(row).get(col).setCellState(CellState.FILLED);
        game.getMoves().add(move);
        game.getWinningStrategy().checkWinner(board, move);
    }

    private boolean isGameDraw(Board board) {
        boolean isBoardFull = true;
        for (int i = 0; i < board.getDimension(); i++) {
            for (int j = 0; j < board.getDimension(); j++) {
                if (!board.getBoard().get(i).get(j).getCellState().equals(CellState.FILLED)) {
                    isBoardFull = false;
                    break;
                }
            }
        }
        return isBoardFull;
    }
}
