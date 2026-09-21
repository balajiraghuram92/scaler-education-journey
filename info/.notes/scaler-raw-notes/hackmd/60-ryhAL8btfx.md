Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/ryhAL8btfx

Pre-Reads: Machine Coding - 13: Code Splitwise 1

Context
This session picks up directly from Design Splitwise's requirements list (R1-R12), staying in the same roleplayed-interview frame while shifting from algorithm design into actual class-diagram and code work.
A genuinely new technique is introduced today: building a class diagram by spotting nouns directly in written requirements, rather than visualizing the system as done for TicTacToe, Parking Lot, and BookMyShow. This gets deliberate, unhurried treatment since it is new.
Models are built in two passes: BaseModel, User, and Group's plain fields are built live, while Expense, ExpenseUser, and both supporting enums go out as homework against a precise spec built together in class.
Relationship annotations (@ManyToOne, @ManyToMany, mappedBy) are deliberately not added today. Models stay as plain fields, with real relationships becoming their own dedicated segment next class.
Command-line input handling is covered only at the conceptual and pseudocode level today; the real Command/CommandExecutor implementation is next class's work.
No Spring Boot or JPA primer is needed, since that entire stack was already built across BookMyShow, though one meaningful setup difference appears: no persistence needed across runs means an in-memory database and no web layer this time.

Overview
Segment | What is covered | Concepts in play
Recall of Design Splitwise | Confirming the one-line pitch and the greedy get/give settlement algorithm from last session | Continuity recall
The noun-spotting method | A new technique for deriving classes directly from written requirements text, applied to R1 through R12 in order | Requirement-to-class translation
The Transaction trap and the dummy-expense trick | Why R10's "list of transactions" tempts a new Transaction class, and why reusing Expense with a type flag avoids two sources of truth for the same kind of data | Avoiding redundant modeling, single source of truth
Attributes and the paid/owed relationship problem | Recognizing that "who paid what" and "who owed what" are properties of a relationship between User and Expense, not clean attributes of either, leading to a new mapping class, ExpenseUser | Relationship-shaped data, mapping/join classes
Schema design | Turning the class diagram into five real tables, and reapplying the enum-vs-lookup-table test to ExpenseType and ExpenseUserType | Schema translation, enum-vs-configurable-data test
Spinning up the project | Choosing H2 over MySQL since no cross-run persistence is needed, and skipping the web starter since input is CLI-driven, not REST | Tooling choices driven by actual requirements
Live model build | Building BaseModel, User, and Group's plain fields, and finally explaining Lombok's actual compile-time mechanism in depth | JPA base classes, Lombok internals
Command pattern for CLI input | Evolving a naive giant if-else main() into a Command interface plus a CommandExecutor, conceptually, to fix an SRP violation | Single Responsibility Principle, Command design pattern
AI Corner: homework model generation | Everyone generates the remaining models via AI and checks the result against the paid/owed design decision made earlier in the same session | Verifying AI output against a team's own in-session design decisions

Why This Session Matters
Noun-spotting is a faster, more direct technique specifically suited to how real interviews and real product requirements actually arrive, as typed-out text, not something to visualize from scratch. Knowing when to switch techniques based on how information is presented is itself a practical skill.
The dummy-expense trick, recognizing that a new kind of row in an existing table can solve a problem more cleanly than inventing a whole new table, is a transferable modeling instinct that shows up constantly in real schemas (a refund modeled as a negative order, a cancellation modeled as a status change rather than a new entity).
Distinguishing relationship-shaped data (paid/owed, which depends on both a user and an expense together) from attribute-shaped data (a name, a phone number) is the same reasoning already used for BookMyShow's pricing problem, and reinforcing it here confirms it as a genuinely internalized skill rather than a one-off lesson.
Applying the enum-vs-lookup-table test and the reserved-keyword naming fix without being prompted, as happens several times this session, is a concrete sign that earlier lessons have become automatic reflexes rather than memorized facts to be re-derived each time.
AI defaulting to the generic, obvious version of a design (reintroducing the exact Map<User, Integer> structure the class had just deliberately moved away from) is a realistic and important lesson: AI has no visibility into a team's own whiteboard history or prior design decisions, so verification always has to be grounded in what the team itself already decided, not in what looks reasonable in isolation.

Real-World Use Cases
Extracting entities from written requirements: Product managers and engineers routinely derive a data model directly from user stories or a requirements document by pulling out the nouns that need independent tracking, exactly the technique introduced this session for a real interview setting.
Reusing an existing table with a type flag: Real systems commonly model a refund as a negative-amount order row, or a cancellation as a status change on an existing entity, rather than creating a parallel table for every new kind of event, the same reasoning behind treating a settlement as a flagged Expense.
Mapping and join classes for relationship-specific data: Any system where a value depends on two entities together, a student's grade in a specific course, an employee's role on a specific project, models that value on its own join class rather than as a field on either entity alone.
In-memory databases for ephemeral environments: Test suites, demo environments, and short-lived CLI tools commonly use an in-memory database like H2 specifically because nothing needs to survive past the current run, avoiding the operational overhead of a real persistent database.
The Command pattern in CLI tools and REPLs: Git's own command-line interface, and many internal developer tools, are built around a Command-style pattern where each subcommand is its own self-contained class, so adding a new command never requires touching a central dispatcher.
Verifying AI-generated model code against prior team decisions: An engineer reviewing AI-generated code checks it against decisions the team already made in design discussions or documentation, not just against generic best practices, since AI cannot see context that was never part of its prompt.

Connection to the Upcoming Class
Next session opens by comparing everyone's homework attempts at Expense, ExpenseUser, and the two enums, before the class settles on a final version together.
Next session adds real relationship annotations to every model, the work deliberately deferred out of today's session, turning today's plain-field classes into a fully connected JPA schema.
Next session builds the full Settle Up feature end to end, calling directly into the greedy get/give algorithm designed in Design Splitwise.
Next session also wires up the actual Command/CommandExecutor code with real command-line input, replacing today's conceptual pseudocode with a working implementation.

Prerequisites from the Previous Class
The exact wording of R1 through R12: Today's noun-spotting method is applied directly against this list, requirement by requirement, in the same strict order used last session.
The paid-vs-owed sum invariant: The rule that the sum of what people paid must equal the sum of what people owed, for any single expense, underlies why ExpenseUser needs both an amount and a type distinguishing the two roles.
The extra_amount balance computation: Each person's net balance across every expense, computed as total paid minus total owed, is the value the eventual Settle Up feature will compute from the Expense and ExpenseUser data modeled today.
R10 versus R11 scope distinction: Individual settle-up (R10, one person across everything) and group settle-up (R11, one group's own expenses only) are the two use cases the dummy-expense trick and the Group-scoped expense list need to support correctly.
The greedy get/give algorithm: The two-heap, biggest-getter-meets-biggest-giver approach designed last session is the logic the real settlement code will call once relationships and CLI wiring are complete next class.

Key Concept Preview
Not every noun in a requirement becomes a class. Some nouns are attributes of a class you already have, and some describe access rules or behavior that becomes a Service method later, never a new class at all.
A settlement does not need its own Transaction table. Representing it as a specially flagged Expense avoids having two separate sources of truth for the same underlying idea, money moving between people, which would otherwise have to be reconciled every time balances are recalculated.
A value like "how much did this person pay for this expense" is not a clean attribute of either User or Expense alone. It depends on both together, which is exactly the signal that it belongs on its own mapping class, the same reasoning already used for BookMyShow's show-and-seat-type pricing.
The enum-vs-lookup-table test is not about how the values look (short text versus long text). It is about whether the same fixed set of values applies everywhere, or whether different owners in the system would want to define their own distinct sets.
An in-memory database like H2 behaves like a real relational database for the life of one run, with real tables and real SQL underneath, and disappears the moment the application stops. This is the correct fit the moment a system's own requirements confirm that no data needs to survive between runs.

What You Will Walk Away With
Apply the noun-spotting method to derive classes directly from a written requirements document
Distinguish a noun that deserves its own class from one that is merely an attribute or a described behavior
Recognize when a new requirement can reuse an existing entity via a type flag, rather than requiring an entirely new table
Identify when a value depends on the relationship between two entities rather than belonging cleanly to either one, and model it as a mapping class
Apply the enum-vs-lookup-table test to a new scenario and justify the choice
Explain why an in-memory database and no web starter are the correct tooling choices once a system's actual requirements are known
Explain Lombok's actual compile-time mechanism for generating getters and setters, rather than treating it as a vague convenience
Trace the evolution from a monolithic if-else main() to a Command interface and a CommandExecutor, and explain which SRP violation each step fixes
Evaluate AI-generated model code against a team's own prior design decisions, not just against generic correctness
