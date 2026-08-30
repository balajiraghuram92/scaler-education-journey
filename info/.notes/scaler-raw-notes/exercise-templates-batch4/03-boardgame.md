# Implement Factory Design Pattern for Board Game Creation

Source folder: 1773391480_6b97268e6b9c0980/Boardgame-solution

## Problem Statement

You are building a gaming application in which you need to create different type of Games. Depending on the type of game (e.g., TIC TAC TOE, CHESS, SNAKE & LADDER), different type of game objects are required. You need a way to create game object without explicitly specifying their classes, ensuring the application is open for future game types.

Your task is to implement the Factory pattern to create Game objects. The Factory pattern provides a way to create objects without exposing the instantiation logic, allowing for easy addition of new game types.

## Detailed Requirements

### Task 1 - Creating a Common Parent Class - BoardGame

Implement the common parent class named BoardGame. This class should include attributes and methods that are common to all the Games. The method gameType has already been abstracted out for you as an example. You will need to implement the BoardGame class as a common parent class for all Game Types.

### Task 2 - Implementing the Factory Pattern

Implement the BoardGameFactory class that follows the Simple Factory pattern. This class should have a method to create Game object based on the GameType. The factory class should be capable of creating different types of games based on the GameType. Also remember that to create a game, you need to pass the game name as a parameter as well.

### Instructions

- Implement the BoardGame class as a common parent class for all type of Games. Include attributes and methods that are common to all Games.
- Implement the BoardGameFactory class that implements the Simple Factory pattern. Add a method to create game based on GameType and other parameters.

## Graded Contract (from tests)

- **BoardGame abstract class** must have:
  - String field `boardGameName` (any access modifier)
  - Abstract method `gameType()` returning GameType with no parameters
  - Abstract method `playGame()` returning void with no parameters
  - Public getter `getBoardGameName()` returning String
- **BoardGameFactory class** must have:
  - Static method taking GameType and String parameters and returning BoardGame
  - Method name can be any name (tests use reflection to find it)
- **Exactly 3 implementations** of BoardGame class in the package (TIC_TAC_TOE, CHESS, SNAKE_LADDER)
- **GameType enum** with at least: TIC_TAC_TOE, CHESS, SNAKE_LADDER

## Learner Template

### BoardGame (Abstract Parent Class)

```java
package com.example.boardgamecreation;

public abstract class BoardGame {
    private String boardGameName;

    public BoardGame(String boardGameName) {
        this.boardGameName = boardGameName;
    }

    public String getBoardGameName() {
        // TODO: Implement getter
    }

    public abstract void playGame();

    public abstract GameType gameType();
}
```

### GameType (Enum)

```java
package com.example.boardgamecreation;

public enum GameType {
    TIC_TAC_TOE,
    CHESS,
    SNAKE_LADDER
}
```

### BoardGameFactory (Simple Factory)

```java
package com.example.boardgamecreation;

public class BoardGameFactory {
    public static BoardGame createGame(GameType gameType, String boardGameName) {
        // TODO: Implement factory method using switch/if-else to create appropriate game type
        // Should support: TIC_TAC_TOE, CHESS, SNAKE_LADDER
        // Should throw IllegalArgumentException for unsupported game type
    }
}
```

### TicTacToeBoardGame (Concrete Implementation)

```java
package com.example.boardgamecreation;

public class TicTacToeBoardGame extends BoardGame {
    public TicTacToeBoardGame(String boardGameName) {
        super(boardGameName);
    }

    @Override
    public void playGame() {
        // TODO: Implement game-specific logic
    }

    @Override
    public GameType gameType() {
        // TODO: Return GameType.TIC_TAC_TOE
    }
}
```

### ChessBoardGame (Concrete Implementation)

```java
package com.example.boardgamecreation;

public class ChessBoardGame extends BoardGame {
    public ChessBoardGame(String boardGameName) {
        super(boardGameName);
    }

    @Override
    public void playGame() {
        // TODO: Implement game-specific logic
    }

    @Override
    public GameType gameType() {
        // TODO: Return GameType.CHESS
    }
}
```

### SnakeLadderBoardGame (Concrete Implementation)

```java
package com.example.boardgamecreation;

public class SnakeLadderBoardGame extends BoardGame {
    public SnakeLadderBoardGame(String boardGameName) {
        super(boardGameName);
    }

    @Override
    public void playGame() {
        // TODO: Implement game-specific logic
    }

    @Override
    public GameType gameType() {
        // TODO: Return GameType.SNAKE_LADDER
    }
}
```

## Deliberately Left Out (for the learner to design)

- Specific game logic implementations in each playGame() method
- Additional attributes or methods specific to each game type (e.g., board size, player count)
- Error handling or logging in the factory
- Configuration or builder patterns for game initialization
