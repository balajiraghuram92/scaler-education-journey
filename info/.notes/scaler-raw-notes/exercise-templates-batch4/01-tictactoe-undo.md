# TicTacToeUndoFunctionality

Source folder: 1773391402_30606b4ea187d469/Tic_Tac_Toe_Undo-solution

## Problem Statement

Your task is to implement the Tic Tac Toe game with an additional feature: the ability to undo the last move. The game should allow players to undo their moves until the beginning of the game.

## Detailed Requirements

- The game should be for two players: one player is 'X' and the other is 'O'.
- Players take turns to make a move.
- After each move, the game should check for a winner.
- If there is a winner or the board is full, the game should declare the result.
- Players should have an option to undo their last move.
- The game is played on a 3x3 board.
- The game should keep track of the state of the board, the current player, and the history of moves.

## Graded Contract (from tests)

- **GameController.startGame(int dimension, List<Player> players)** — returns a Game instance initialized with given dimension and players
- **GameController.undo(Game game)** — reverts the last move on the board; throws EmptyMovesException if no moves exist
- **Game.getBoard()** — returns the Board
- **Game.getMoves()** — returns List<Move> of all moves made so far
- **Game.getWinningStrategy()** — returns WinningStrategy instance
- **Board.getBoard()** — returns List<List<Cell>> (2D grid)
- **Cell.getRow(), Cell.getCol()** — return position
- **Cell.setPlayer(Player), setPlayer(Player)** — set/get player occupying cell
- **Cell.setCellState(CellState), getCellState()** — set/get EMPTY or FILLED state
- **WinningStrategy.checkWinner(Board, Move)** — returns boolean indicating if move creates a win condition
- **CellState enum** — must have EMPTY and FILLED values
- **Move(Player, Cell)** — constructor for recording a move
- **Symbol(char)** — constructor taking a character symbol
- **EmptyMovesException** — thrown when undo() called on empty moves list with message "Undo operation can't be performed as the moves list is empty"

## Learner Template

### GameController

```java
package com.example.tttundo.controllers;

import com.example.tttundo.exceptions.EmptyMovesException;
import com.example.tttundo.exceptions.InvalidMoveException;
import com.example.tttundo.models.Game;
import com.example.tttundo.models.GameState;
import com.example.tttundo.models.Player;

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

    public void undo(Game game) throws EmptyMovesException {
        // TODO: Implement
    }

    public GameState getGameState(Game game) {
        // TODO: Implement
    }
}
```

### Game

```java
package com.example.tttundo.models;

import com.example.tttundo.exceptions.EmptyMovesException;
import com.example.tttundo.strategies.WinningStrategy;

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

    public void makeMove() throws InvalidMoveException {
        // TODO: Implement turn-based move logic, validation, win checking
    }

    public void undo() throws EmptyMovesException {
        // TODO: Implement undo logic: remove last move, restore board, restore game state
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
package com.example.tttundo.models;

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

    public void undoMove(Move move) {
        // TODO: Reset cell at move position to EMPTY and null player
    }
}
```

### Cell

```java
package com.example.tttundo.models;

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
package com.example.tttundo.models;

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
package com.example.tttundo.models;

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
package com.example.tttundo.models;

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
package com.example.tttundo.models;

public enum CellState {
    EMPTY,
    FILLED
}
```

### GameState

```java
package com.example.tttundo.models;

public enum GameState {
    IN_PROGRESS,
    ENDED,
    DRAW
}
```

### WinningStrategy

```java
package com.example.tttundo.strategies;

import com.example.tttundo.models.Board;
import com.example.tttundo.models.Move;

public interface WinningStrategy {
    boolean checkWinner(Board board, Move move);
}
```

### Exceptions

```java
// EmptyMovesException.java
package com.example.tttundo.exceptions;

public class EmptyMovesException extends Exception {
    public EmptyMovesException(String message) {
        super(message);
    }
}

// InvalidMoveException.java
package com.example.tttundo.exceptions;

public class InvalidMoveException extends Exception {
    public InvalidMoveException(String message) {
        super(message);
    }
}

// GameInvalidationException.java
package com.example.tttundo.exceptions;

public class GameInvalidationException extends Exception {
    public GameInvalidationException(String message) {
        super(message);
    }
}
```

## Deliberately Left Out (for the learner to design)

- **WinningStrategyImpl** — full win-checking logic for rows, columns, and diagonals
- **Bot class** — AI player implementation (if required)
- **Game.validateMove()** — boundary and cell occupancy validation
- **Game.displayBoard()** — board visualization
- **Undo state management** — the specific algorithm for reverting game state (tracking nextPlayerMoveIndex, resetting winner, gameState on undo)
- **Main entry point** — game loop and user interaction flow
