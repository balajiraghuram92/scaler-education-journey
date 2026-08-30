Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/HkgO_hZwzx

# TicTacToe Machine Coding Implementation Guide

## Overview

This document builds on prior design work to implement TicTacToe in Java, focusing on two key areas: efficiently checking for winners and writing the foundational code.

## Winner-Checking Algorithm Optimization

The document presents a four-step optimization for checking if a move creates a winning condition:

**Solution 1: Brute Force** – Check every player against the entire board (rows, columns, diagonals) after each move, yielding O(N³) complexity.

**Solution 2: Check Only Current Player** – Since only the player who just moved could have won, eliminate the per-player loop, reducing to O(N²).

**Solution 3: Check Only Touched Lines** – A move at position (i, j) can only affect row i, column j, and potentially two diagonals. Determine diagonal involvement via conditions: i == j (main diagonal) and i + j == N-1 (anti-diagonal). This achieves O(N) time.

**Solution 4: Running Counters** – Rather than rescanning lines, maintain counters per row, column, and diagonal. Increment the relevant counter when a symbol is placed and check if it equals N. This achieves O(1) per move with O(N) space overhead (2N + 2 total maps).

## Code Implementation

The folder structure organizes files by responsibility:

```
controllers/
exceptions/
factory/
models/
strategies/
  botplayingstrategies/
  winningstrategies/
```

### Key Classes

**Enums (No Dependencies)**
- PlayerType: HUMAN, BOT
- BotDifficultyLevel: EASY, MEDIUM, HARD
- GameState: IN_PROGRESS, ENDED, DRAW
- CellState: EMPTY, FILLED

**Core Models**
- Symbol: Wraps a character representing a player's mark
- Cell: Contains row, column, state, and player reference; initializes as EMPTY
- Board: Creates N×N grid of Cells in constructor
- Move: Pairs a Player with a Cell
- Player: Abstract base; contains makeMove() returning a Move

**Game Class**
The centerpiece uses the Builder pattern exclusively via private constructor and `Game.getBuilder()`. The Builder validates:
- Bot count (maximum 1 per game)
- Player count (must equal dimension - 1)
- Unique symbols across all players

The `makeMove()` method validates the move, updates cell state, checks for winner using all WinningStrategy implementations, and detects draws when board fills.

**Interfaces and Factories**
- WinningStrategy: Interface with `checkWinner(Board board, Move move)` signature
- BotPlayingStrategyFactory: Maps difficulty level to strategy (written as forward reference; actual strategies incomplete)

**GameController**
- `startGame()`: Chains Builder methods
- `makeMove()`: Left as stub (depends on complete winning strategies)
- `printBoard()`, `getGameState()`, `getWinner()`: Delegation methods

### Critical Design Decisions

**Why Private Game Constructor?** Prevents unvalidated object creation; all instances must pass Builder validation before existing.

**Why Cells Created Upfront?** Every position must be queryable before move validation; nonexistent cells cannot report their state.

**Why CellState Enum?** Unlike boolean, an enum can expand to accommodate future states (e.g., BLOCKED) without restructuring.

**Why WinningStrategy List?** New winning rules can be added by creating one new class without touching Game's logic.

## Deliberately Incomplete Sections

- RowWinningStrategy, ColWinningStrategy, DiagonalWinningStrategy (awaiting O(1) running-count implementations)
- Bot.java and three BotPlayingStrategy implementations (blocked on strategy structure)
- GameController.makeMove() wired implementation (causes issues without complete strategies)
- validateUniquePlayerSymbols() in Builder (marked for homework)

## Key Insights

The document emphasizes that optimization from O(N³) to O(1) eliminated three sources of waste progressively: checking multiple players, scanning untouched lines, and re-scanning lines already checked. For TicTacToe's bounded N, accepting O(N) additional space for O(1) move checking is a sound tradeoff.

The implementation discipline prioritizes design coherence over compilation status; forward references and stubs are intentional checkpoints, not oversights.
