# TicTacToe Winner Checker Functionality

Source folder: 1773391407_c738ae23517c4a32/TTT_Winner_Check-solution

## Problem Statement

Your task is to implement the Tic Tac Toe game with an additional feature: the ability to check the winner after every move. The game should be able to check the winner after every move.

## Detailed Requirements

- The game should be for two players: one player is 'X' and the other is 'O'.
- Players take turns to make a move.
- After each move, the game should check for a winner.
- If there is a winner or the board is full, the game should declare the result.
- The game is played on a 3x3 board.
- The game should keep track of the state of the board, the current player, and the history of moves.

## Graded Contract (from tests)

- **GameController.startGame(int dimension, List<Player> players)** — returns a Game instance initialized with given dimension and players
- **Game.validateMove(Move move)** — returns boolean indicating if move is valid (within bounds and cell is EMPTY)
- **Game.getMoves()** — returns List<Move> of all moves made so far
- **Game.getWinningStrategy()** — returns WinningStrategy instance
- **Game.getBoard()** — returns the Board
- **Board.getBoard()** — returns List<List<Cell>> (2D grid)
- **Board.getDimension()** — returns board dimension
- **Cell.getRow(), Cell.getCol()** — return position
- **Cell.setPlayer(Player), getPlayer()** — set/get player occupying cell
- **Cell.setCellState(CellState), getCellState()** — set/get EMPTY or FILLED state
- **WinningStrategy.checkWinner(Board, Move)** — returns boolean indicating if move creates a win condition (checks rows, columns, and diagonals)
- **CellState enum** — must have EMPTY and FILLED values
- **Move(Player, Cell)** — constructor for recording a move
- **Symbol(char)** — constructor taking a character symbol
- **InvalidMoveException** — thrown when move violates board rules with message "Invalid move made by the Player"

## Learner Template

### GameController

```java
package com.example.tttwinnerchecker.controllers;

import com.example.tttwinnerchecker.exceptions.InvalidMoveException;
import com.example.tttwinnerchecker.models.Game;
import com.example.tttwinnerchecker.models.GameState;
import com.example.tttwinnerchecker.models.Player;

import java.util.List;

public class GameController {
    public Game startGame(int dimension, List<Player> players) throws Exception {
        // TODO: Implement using Game.getBuilder() pattern
    }

    public void makeMove(Game game) throws InvalidMoveException {
        // TODO: Implement
    }

    public void displayBoard(Game game) {
        // TODO: Implement
    }

    public Player getWinner(Game game) {
        // TODO: Implement
    }

    public GameState getGameState(Game game) {
        // TODO: Implement
    }
}
```

### Game

```java
package com.example.tttwinnerchecker.models;

import com.example.tttwinnerchecker.exceptions.InvalidMoveException;
import com.example.tttwinnerchecker.strategies.WinningStrategy;

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
        // TODO: Implement constructor initialization
    }

    public static Builder getBuilder() {
        // TODO: Implement builder pattern
    }

    public Board getBoard() {
        // TODO: Implement
    }

    public List<Player> getPlayers() {
        // TODO: Implement
    }

    public GameState getGameState() {
        // TODO: Implement
    }

    public Player getWinner() {
        // TODO: Implement
    }

    public int getNextPlayerMoveIndex() {
        // TODO: Implement
    }

    public List<Move> getMoves() {
        // TODO: Implement
    }

    public WinningStrategy getWinningStrategy() {
        // TODO: Implement
    }

    public boolean validateMove(Move move) {
        // TODO: Implement move validation (check bounds and cell is EMPTY)
    }

    public void makeMove() throws InvalidMoveException {
        // TODO: Implement turn-based move logic, validation, win checking
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

        public Game build() throws Exception {
            // TODO: Implement validation and construction
        }
    }
}
```

### Board

```java
package com.example.tttwinnerchecker.models;

import java.util.List;

public class Board {
    private int dimension;
    private List<List<Cell>> board;

    public Board(int dimension) {
        // TODO: Initialize board with empty cells at correct positions
    }

    public int getDimension() {
        // TODO: Implement
    }

    public List<List<Cell>> getBoard() {
        // TODO: Implement
    }

    public void displayBoard() {
        // TODO: Implement board display (EMPTY shows as "|  |", FILLED shows player symbol)
    }
}
```

### Cell

```java
package com.example.tttwinnerchecker.models;

public class Cell {
    private int row;
    private int col;
    private Player player;
    private CellState cellState;

    public Cell(int row, int col) {
        this.row = row;
        this.col = col;
        this.cellState = CellState.EMPTY;
    }

    public int getRow() {
        // TODO: Implement
    }

    public int getCol() {
        // TODO: Implement
    }

    public Player getPlayer() {
        // TODO: Implement
    }

    public void setPlayer(Player player) {
        // TODO: Implement
    }

    public CellState getCellState() {
        // TODO: Implement
    }

    public void setCellState(CellState cellState) {
        // TODO: Implement
    }
}
```

### Move

```java
package com.example.tttwinnerchecker.models;

public class Move {
    private Player player;
    private Cell cell;

    public Move(Player player, Cell cell) {
        this.player = player;
        this.cell = cell;
    }

    public Player getPlayer() {
        // TODO: Implement
    }

    public Cell getCell() {
        // TODO: Implement
    }
}
```

### Player

```java
package com.example.tttwinnerchecker.models;

public class Player {
    private String name;
    private Symbol symbol;

    public Player(String name, Symbol symbol) {
        this.name = name;
        this.symbol = symbol;
    }

    public String getName() {
        // TODO: Implement
    }

    public Symbol getSymbol() {
        // TODO: Implement
    }

    public Move makeMove(Board board) {
        // TODO: Implement user input logic to get row/col and create Move
    }
}
```

### Symbol

```java
package com.example.tttwinnerchecker.models;

public class Symbol {
    private char symbol;

    public Symbol(char symbol) {
        this.symbol = symbol;
    }

    public char getSymbol() {
        // TODO: Implement
    }
}
```

### CellState

```java
package com.example.tttwinnerchecker.models;

public enum CellState {
    EMPTY,
    FILLED
}
```

### GameState

```java
package com.example.tttwinnerchecker.models;

public enum GameState {
    IN_PROGRESS,
    ENDED,
    DRAW
}
```

### WinningStrategy

```java
package com.example.tttwinnerchecker.strategies;

import com.example.tttwinnerchecker.models.Board;
import com.example.tttwinnerchecker.models.Move;

public interface WinningStrategy {
    boolean checkWinner(Board board, Move move);
}
```

### Exceptions

```java
// InvalidMoveException.java
package com.example.tttwinnerchecker.exceptions;

public class InvalidMoveException extends Exception {
    public InvalidMoveException(String message) {
        super(message);
    }
}

// GameInvalidationException.java
package com.example.tttwinnerchecker.exceptions;

public class GameInvalidationException extends Exception {
    public GameInvalidationException(String message) {
        super(message);
    }
}
```

## Deliberately Left Out (for the learner to design)

- **WinningStrategyImpl** — full win-checking logic for rows, columns, and diagonals
- **Bot class** — AI player implementation (if required)
- **Game.displayBoard()** — board visualization
- **Draw detection** — logic to check if board is full (tested in testGameWinningCase4)
- **Main entry point** — game loop and user interaction flow
