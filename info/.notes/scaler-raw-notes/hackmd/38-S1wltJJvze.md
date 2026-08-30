Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/S1wltJJvze

Title: Pre-Reads-AppliedDesignMachineCoding-02 - HackMD
URL: https://hackmd.io
Source element: <body>
---
Pre-Reads-AppliedDesignMachineCoding-02
Tushar Harsan·Follow
Last edited by
Tushar Harsan
on
Aug 16, 2026
PRE-READ	Applied Design & Machine Coding	Machine Coding - 2: Design TicTacToe
Context
Last session delivered a 6-step framework (Overview, Gather, Clarify, Class Diagram, Schema Diagram, Code) but only exercised the first two diagram-related steps, using the Vehicle example.
This session fills in the two missing tools before using anything: how to turn a class diagram into a database schema, and how to structure code using MVC with a specific build order.
Once both tools are in hand, the session runs all six steps, start to finish, on one large example: TicTacToe generalized to an N x N board, with bots and a global undo feature. Note that "just build TicTacToe" is explicitly treated as never the real interview ask.
The teaching approach mirrors last session: problem-first, one running example carried through every step, with the same UML notation from the earlier UML lecture reused rather than reinvented.
AI Corner returns to a reviewer role rather than a generator role, matching last session's framing that AI sharpens design thinking, it does not replace it.
Overview
Segment	What is covered	Concepts in play
Schema design algorithm	A repeatable process for turning any class into database tables: simple attributes become columns directly, class-typed attributes require a cardinality check first	Cardinality (1:1, 1:M, M:M), foreign keys, junction tables
MVC architecture and build order	Correct layering (Controller to Service to Repository) and, more importantly, a build order that finishes one requirement completely before starting the next	Separation of concerns, models-first sequencing
TicTacToe Step 0: Overview	Confirming this is a full system (not pure entity design), no persistence needed, and a hardcoded main-method interaction is sufficient	Entity vs system, the three clarifying questions reused
TicTacToe Step 1: Requirements gathering	Seven suggested requirements: N x N board, N-1 players, unique symbols, one bot with difficulty levels, randomized turn order, generalized win condition, and a global undo	Suggestion-led requirements, generalization over hardcoding
Deep dive: the Undo feature	Three progressively better approaches to undo (direct reversal, full replay, state snapshots) compared on correctness, time cost, and space cost	Time-space tradeoff, designing for side effects
Class diagram built live	Combining noun-spotting with a step-by-step walkthrough of gameplay to derive every class, enum, and interface, applying Builder, Factory, and two uses of Strategy	Builder, Factory, Strategy, enum-over-boolean, composition/aggregation
Polishing the design with AI	Using AI only after the design is complete, to catch small gaps and generate a diagram picture to check against the whiteboard version	AI as a late-stage checker, not an originator
AI Corner: spotting mistakes in code	Reviewing a deliberately flawed Game class, having AI diagnose the problems, then fixing it using the class diagram already built	SRP, OCP, MVC-separation violations
Why This Session Matters
Schema design under time pressure is a common failure point. Engineers who don't have a fast, repeatable rule for cardinality tend to either over-normalize simple relationships or under-normalize many-to-many ones, both of which cost visible time in a live round.
The build-order habit (finish one requirement fully before starting the next) directly affects how an interview gets scored. A candidate with three fully working features scores higher than one with six half-built layers, even though the second candidate "touched" more code.
Generalizing a familiar problem (3x3 TicTacToe becomes N x N) is a recurring interview pattern. Interviewers deliberately pick well-known games or systems specifically to see whether a candidate defaults to the trivial hardcoded version or proactively generalizes it.
The undo feature is a genuine design decision with real tradeoffs, not a solved problem. Being able to name multiple approaches and justify a choice based on the actual constraints (board size, state size) is exactly the kind of judgment senior reviews look for.
Using AI only after a design is fully worked out, and using it to find flaws rather than to generate a first draft, is a discipline that protects genuine design skill from atrophy, a concern equally relevant in real engineering work as in interview prep.
Real-World Use Cases
Schema design algorithm: A social media platform mapping a Post class with a List<Comment> field applies the same one-to-many rule used for Movie and Review, placing a foreign key on the comments table rather than building an unnecessary junction table.
MVC build order: A backend engineer building a checkout flow under a sprint deadline finishes the payment confirmation feature completely (controller, service, repository) before starting the refund feature, rather than leaving both half-wired, mirroring the interview-time strategy taught here.
Generalizing a familiar system: A ride-sharing platform's matching engine is built to handle any number of vehicle types and pricing tiers from day one, rather than hardcoded for one city's initial two options, the same instinct behind generalizing TicTacToe to N x N.
Undo feature tradeoffs: A word processor's undo stack keeps periodic full-document snapshots rather than replaying every keystroke from the beginning, accepting extra memory for instant undo, exactly the reasoning applied to picking the snapshot approach for TicTacToe.
Strategy pattern for extensible rules: A fraud detection system runs a list of independent rule-checking strategies against every transaction, so a new fraud pattern can be added as a new strategy class without modifying the core transaction-processing class, mirroring WinningStrategy.
AI as a design reviewer: A backend team lead pastes a teammate's draft class design into an AI tool and asks it to flag SRP or OCP violations before code review, using AI to sharpen a review rather than to write the design itself.
Connection to the Upcoming Class
The next session, Code TicTacToe 1, picks up exactly where this one stops: the design and pattern choices are already finalized, so the next class is pure execution.
The build order taught in Section 2 (models first, then one requirement fully working at a time, Controller to Service to Repository) is the literal sequence that will be followed live in the next session's coding.
Every pattern chosen today (Builder for game creation, Factory for player creation, Strategy for bot difficulty and winning conditions) will be implemented as real working classes next class, not re-derived.
The undo approach selected today (state snapshots) becomes a concrete implementation task next class, so the reasoning behind picking it should already feel settled before that session starts.
Prerequisites from the Previous Class
The 6-step framework
Overview, Gather, Clarify, Class Diagram, Schema Diagram, Code, only the first two diagram steps were exercised previously; this session completes the remaining steps.
Entity vs system judgment
The three clarifying questions (what am I designing, do I need persistence, how does a user interact) are reused directly for TicTacToe's overview step.
Leading requirements with suggestions
The habit of proposing features with rationale rather than asking "what should I support" carries over unchanged into TicTacToe's seven requirements.
Enum over boolean for extensibility
The transmission-type lesson from the Vehicle example is directly reapplied to CellState and PlayerType in this session.
UML notation
Three-compartment class boxes, <<interface>> stereotypes, italics for abstract classes, solid and dashed arrows with hollow triangle arrowheads, filled diamonds for composition and hollow diamonds for aggregation.
The specific test for composition versus aggregation (does the part mean anything if the whole is destroyed) is reused directly for Game-Board (composition) versus Game-Player (aggregation).
LSP-driven interface separation
The Refuelable/Chargeable split from the Vehicle lecture is the same reasoning behind not forcing shared behavior onto classes that do not need it, referenced implicitly in how Player is split into HumanPlayer and BotPlayer.
Key Concept Preview

A class attribute only needs a cardinality check if it refers to another class. Simple values (numbers, strings, booleans) always become columns directly, no exceptions.

A many-to-many relationship needs a separate mapping table. A one-to-many relationship never does, the foreign key just goes on the "many" side. Confusing these two is the single most common schema-design slip under time pressure.

Building every model, then every controller, then every service, then every repository, feels systematic but is actually the riskier order. If time runs out, nothing works end to end. Finishing one requirement completely before starting the next protects against exactly this failure mode.

Undo is not one fixed technique, it is a genuine tradeoff between correctness, time, and space. The "obvious" approach (clear the last cell) silently breaks the moment a move has side effects elsewhere on the board.

A composition relationship between two classes never automatically justifies giving one of them a new interface or capability. This same instinct from the Vehicle lecture returns here in deciding what belongs on Player versus what belongs on a separate Strategy interface.

What You Will Walk Away With
Learning Outcome
Apply a repeatable algorithm to convert any class diagram into database tables, correctly distinguishing 1:1, 1:M, and M:M relationships
Explain why a models-first, one-requirement-at-a-time build order scores better than building all layers in parallel under time pressure
Confirm system-level scope (persistence, interaction mode) for a familiar problem using the same clarifying questions applied to unfamiliar ones
Generalize a familiar problem statement (fixed-size TicTacToe) into its scalable form (N x N) as a default instinct, not an afterthought
Compare at least three approaches to implementing an undo feature and justify a choice based on actual time and space constraints
Construct a class diagram for a mixed physical-and-process system using both noun-spotting and a step-by-step walkthrough
Identify where Builder, Factory, and Strategy patterns naturally emerge from stated requirements rather than being forced onto a design
Diagnose SRP, OCP, and MVC-separation violations in a flawed class, and connect each diagnosis back to a concept already covered
Use AI as a late-stage reviewer and diagram-generator only after a design is fully self-derived
Last changed by 
 
Tushar Harsan·Follow
0
32
Add a comment
Published on  HackMD
