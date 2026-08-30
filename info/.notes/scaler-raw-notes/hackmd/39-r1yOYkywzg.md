Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/r1yOYkywzg

# Content Summary: Machine Coding - TicTacToe Design Document (Post-Read)

This HackMD page contains an extensive educational post-read on system design for a TicTacToe game.

## Main Sections

**Introduction & Framework**: Builds on a 6-step design process (overview, gather requirements, clarify scope, class diagram, schema diagram, code structure) using TicTacToe as the running example.

**Schema Design Algorithm**: Teaches the three-step process for converting class diagrams to database schemas: "Every class becomes a table. Every SIMPLE attribute becomes a column directly. Every attribute that is ANOTHER CLASS needs its cardinality checked first."

**MVC Architecture**: Explains layered code structure with controllers, services, and repositories, emphasizing completing one requirement fully rather than building horizontally across all requirements.

**TicTacToe Design Deep Dive**: Covers:
- Seven requirements (N×N board, N-1 players, unique symbols, bots with difficulty levels, randomized turn order, win conditions, undo feature)
- Three undo approaches with tradeoffs analyzed
- Complete class diagram with proper UML notation
- Design patterns: Builder (game creation), Factory (player instantiation), Strategy (bot difficulty and winning conditions)

**AI Integration**: Demonstrates using AI to review flawed code rather than generate it, identifying violations of Single Responsibility Principle, Open-Closed Principle, and boolean-vs-enum modeling mistakes.

**Pedagogical Elements**: Includes quiz recaps, hidden pitfalls, terminology tables, FAQs, self-check questions, and homework assignments.

The document emphasizes design discipline, separation of concerns, and principled decision-making before implementation.

Note: This is a summary reconstruction — the first fetch attempt hit a broken-images placeholder on the source page; a retry recovered the actual text content above, but it is a summary, not a verbatim capture. Re-fetch directly from the source URL if exact original wording/code blocks are needed.
