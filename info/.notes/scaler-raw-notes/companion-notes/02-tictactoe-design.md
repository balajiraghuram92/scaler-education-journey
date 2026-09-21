Source: Downloads/machine-coding/lesson_2.txt (Scaler Companion AI-generated class revision notes)

Revision Notes: Designing Tic-Tac-Toe
Introduction
In this class, we undertook a detailed case study on designing a Tic-Tac-Toe game, a common problem in software design interviews. We focused on understanding schema design approaches, applying the MVC architecture, and crafting comprehensive class diagrams.

Steps in Software Design
Step 1: Aligning with the Interviewer
Clarify Requirements: Start by aligning with the interviewer, gathering and clarifying requirements .
Step 2: Class Diagram
Cardinality Relationships: Understand the relationships between classes, like instructor to batch relationships .
Two Methods: Identify nouns from requirements or through visualization (a game’s structure or user journey) .
Step 3: Schema Design
Steps: After class diagrams, move to schema design, identifying class relationships and cardinalities .
Designing a Tic-Tac-Toe
Requirements
Board Size: N x N board instead of a fixed 3x3 .
Player Count: N-1 players to ensure the game remains engaging as N increases .
Unique Symbols: Each player has a unique symbol .
Two Player Types: Players can be Human or Bot; Bot players have varying difficulties implemented using the Strategy pattern .
Undo Feature
Three approaches discussed:
Direct Reversal: Clearing the last move on the board. Works well for simple games like Tic-Tac-Toe but not for those with complex side effects (e.g., Chess)【6:5†source】.
Replay from Scratch: Clearing the board and replaying all moves after an undo — better for games with complex rules【6:6†source】.
Snapshot Saving: Most efficient for Tic-Tac-Toe. Saves the board state after every move .
Class Diagram Components
Game Class: Central class interconnected with Board, Player, Move objects. Utilizes Builder and Factory patterns for robust construction and management .
Board and Cell Hierarchy: Compositional relationships where the board contains cells. Cells are enriched with attributes like Row, Column, and CellState .
Player Hierarchy: Abstract Player class with HumanPlayer and BotPlayer subclasses. Enum for PlayerType to avoid boolean simplification issues .
Patterns Used
Builder Pattern: For creating game instances with validation checks.
Strategy Pattern: To implement various bot playing difficulties and winning strategies .
Factory Pattern: For deciding between creating a HumanPlayer or a BotPlayer .
Conclusion
Throughout this class, the emphasis was placed on understanding the underlying structure through UML diagrams and systematically approaching the design problem. Each feature and requirement was evaluated for trade-offs to ensure robust design choices suitable for practical implementations .