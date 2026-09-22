# Implement Factory Design Pattern for Board Game Creation.

## Problem Statement
You are building a gaming application in which you need to create different type of Games. Depending on the type of game (e.g., TIC TAC TOE, CHESS, SNAKE & LADDER), different type of game objects are required. You need a way to create game object without explicitly specifying their classes, ensuring the application is open for future game types.

Your task is to implement the Factory pattern to create Game objects. The Factory pattern provides a way to create objects without exposing the instantiation logic, allowing for easy addition of new game types.

### Task 1 - Creating a Common Parent Class - BoardGame
To streamline the creation of Board Games, implement the common parent class named BoardGame. This class should include attributes and methods that are common to all the Games. The method gameType has already been abstracted out for you as an example. You will need to implement the BoardGame class as a common parent class for all Game Types.

### Task 2 - Implementing the Factory Pattern
Implement the BoardGameFactory class that follows the Simple Factory pattern. This class should have a method to create Game object based on the GameType. The factory class should be capable of creating different types of games based on the GameType. Also remember that to create a game, you need to pass the game name as a parameter as well.

### Instructions
* Implement the BoardGame class as a common parent class for all type of Games. Include attributes and methods that are common to all Games.

* Implement the BoardGameFactory class that implements the Simple Factory pattern. Add a method to create game based on GameType and other parameters.
