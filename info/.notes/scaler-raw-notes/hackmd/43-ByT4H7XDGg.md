Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/ByT4H7XDGg

# Summary of Machine Coding - 4: Code TicTacToe 2

## Core Implementation Gaps Addressed

This document completes three intentional gaps from Post-Read 3:

1. **Winning strategy implementations** (Row, Column, Diagonal)
2. **Bot logic and difficulty strategies**
3. **Controller wiring to enable actual gameplay**

## Key Technical Decisions

### Running-Count Approach
As noted, "the map needs to be a field on the class itself, not something created fresh inside the method" to persist counts across multiple `checkWinner()` calls, maintaining the O(1) efficiency established previously.

### Winning Strategies Structure
- **RowWinningStrategy & ColWinningStrategy**: Use nested maps (row/column index → symbol → count)
- **DiagonalWinningStrategy**: Maintains exactly two maps (main and anti-diagonal) regardless of board size

### Bot Architecture
`Bot` extends `Player` and delegates move calculation to `BotPlayingStrategy` implementations, maintaining separation of concerns. The strategy returns moves with `player` set to `null`; `Bot.makeMove()` patches in the player afterward.

### Strategy Implementations
- **EasyBotPlayingStrategy**: Plays first available empty cell
- **HardBotPlayingStrategy**: Uses minimax algorithm with alpha-beta pruning

## AI Corner Verification Checklist

The document emphasizes four verification steps for AI-generated code:

1. Interface and contract matching
2. Existing codebase conventions compliance
3. Edge case handling
4. Real-world performance constraints

## Known Limitations

The document explicitly acknowledges two honest gaps:

- Invalid player input currently crashes the program rather than prompting retry
- `MediumBotPlayingStrategy` remains a stub
- Unbounded minimax may perform poorly on larger boards

## Self-Assessment Resources

The document provides extensive self-check questions, interview preparation material, and homework assignments for deepening understanding of the completed system.