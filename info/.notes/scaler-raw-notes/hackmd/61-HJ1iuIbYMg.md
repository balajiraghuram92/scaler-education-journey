Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/HJ1iuIbYMg

Post Read : Machine Coding - 13: Code Splitwise 1
Tushar Harsan·Follow
Last edited by
Tushar Harsan
on
Sep 11, 2026
POST-READ	Applied Design & Machine Coding	Machine Coding - 13: Code Splitwise 1
Introduction

Session 12 (Design Splitwise) closed out the entire algorithmic core of this system without touching the class diagram at all: it locked in requirements R1 through R12 in strict order, derived the "sum(paid) = sum(owed)" invariant, built the extra_amount formula for computing each person's true net balance across every expense, walked through the brute-force sorted-chain settlement (correct but socially awkward, 
𝑛
−
1
 transactions), and then fixed it with the greedy get/give two-heap approach (
𝑂
(
𝑛
log
⁡
𝑛
)
, same 
𝑛
−
1
 upper bound, far more sensible pairings). It also named, explicitly, that minimizing settlement transactions to the true mathematical minimum is NP-hard. No formal Post-Read document for session 12 exists yet as of this writing, so session-12 material is cross-referenced directly against its own script in this document rather than against a numbered Post-Read section.

Today's session, Code Splitwise 1, is where the structural side of Splitwise finally gets built: the class diagram (via a genuinely new technique, noun-spotting on a written requirements document), the schema, a fresh Spring Boot project, the first three model classes typed live (BaseModel, User, Group), and the conceptual architecture for taking command-line input (the Command / CommandExecutor split). The running example throughout is Splitwise itself: User, Group, Expense, and the new mapping class ExpenseUser.

Two structural departures from the series' usual shape, stated plainly: there was no live class diagram in session 12 (that structural choice was itself session 12's own departure, and today is where that deferred work happens), and there is no JPA/Spring Boot primer today, since that entire stack was already built and explained across BookMyShow's sessions (Post-Reads 8 and 9). Today's script contains zero real 🎬 Animation blocks; every visual is a static image or hand-drawn board diagram, embedded directly with no invented narration.

This document goes beyond a straight transcription of the live script in two clearly flagged places: a full first-principles teaching of the Command design pattern (the script builds it live through reasoning but never names it as a known, interview-askable GoF pattern), placed in Section 8 where the pattern's structure crystallizes; and a deep-dive on the discriminator-column / single-table schema pattern (the general technique the "dummy expense" trick is a specific instance of), placed in Section 3 right after that trick is introduced.

SECTION 1 — Recall: Design Splitwise
What It Means
Splitwise is an expense-tracking and expense-sharing application: users log who paid what and who owes what, the app tracks running balances as more expenses are added, and "settle up" produces a concrete list of transactions that would zero out a balance.
The hard problem in this system was never structural, it was algorithmic: given a group's final balances, settle everyone using as few transactions as possible.
Session 12 established the core invariant that everything else depends on: for any single, correctly-entered expense, 
∑
paid
=
∑
owed
, and both must equal the total expense amount.
Each person's true net position across every expense they're part of is computed with:

extra\_amount
(
𝑝
𝑒
𝑟
𝑠
𝑜
𝑛
)
=
∑
expenses
(
paid
(
𝑝
𝑒
𝑟
𝑠
𝑜
𝑛
)
−
owed
(
𝑝
𝑒
𝑟
𝑠
𝑜
𝑛
)
)

A positive extra_amount means the person is owed money overall (they put in more than their fair share). A negative value means they owe money overall.
Because the paid/owed invariant holds for every single expense, summing extra_amount across every person in a group must always land on exactly zero. This is a genuine correctness check worth building into real code: if your computed balances don't sum to zero, there is a bug in either the input or the calculation.
Two settlement solutions were built:
Solution 1 (sorted chain): sort everyone by final balance, walk left to right, each person settles fully with their neighbor. Always exactly 
𝑛
−
1
 transactions. Mathematically correct, but pairs people arbitrarily; you could end up owing money to someone you never actually transacted with.
Solution 2 (greedy get/give): split people into a GET pool (positive balance) and a GIVE pool (negative balance). Each round, the biggest getter and biggest giver settle for 
min
(
get
,
give
)
, guaranteeing at least one side fully clears. Implemented with a max-heap for GET and a min-heap for GIVE, giving 
𝑂
(
𝑛
log
⁡
𝑛
)
 total time, with an upper bound (not a guarantee) of 
𝑛
−
1
 transactions.
Minimizing transactions to the true mathematical minimum is NP-hard: no known polynomial-time algorithm guarantees the fewest possible transactions for every input. The greedy approach is a practical, fast approximation, not an exact solver.
Hidden Pitfalls
Treating extra_amount as optional bookkeeping. Skipping straight to "who pays whom" without first computing net balances across all expenses causes exactly the per-expense settlement bug this session's AI Corner catches in Section 9: settling expense-by-expense throws away legitimate cancellations between two people.
Assuming greedy get/give guarantees the true minimum. It only guarantees an upper bound of 
𝑛
−
1
 transactions; the actual minimum is NP-hard to compute exactly, and greedy can sometimes use more transactions than an optimal (but computationally expensive) solution would.
Forgetting the zero-sum sanity check. Not verifying that summed balances equal zero after computing extra_amount for a whole group means a silent data or logic bug can go undetected indefinitely.
SECTION 2 — Administrative Note: Contest Announcement

A short mid-lecture logistics beat: the instructor reads and posts a contest-announcement message in the class communication channel, announcing that the Low-Level Design (LLD) Contest unlocks soon, with tips to focus on code structure, modularity, and efficiency. This has no design content and needs no further reconstruction; it is purely a scheduling/administrative interruption before returning to Splitwise.

SECTION 3 — Class Diagram: The Noun-Spotting Method
What It Means
Every class diagram built so far in this series (TicTacToe, Parking Lot, BookMyShow) was built by visualizing the system: picturing the real-world object and walking through it outside-in.
Splitwise introduces a genuinely different, second technique: noun-spotting. When requirements arrive as a precise, typed-out, numbered list (exactly how real machine-coding interviews usually hand them to you), reading each requirement's own wording and pulling out its nouns directly is often faster than visualizing from scratch.
The method, as a repeatable algorithm:
NOUN-SPOTTING METHOD:
1. Go through every requirement, one at a time.
2. Pull out the nouns.
3. For each noun, ask: "do I need to STORE information about this?"
   - Yes -> it's a real class.
   - No, it's just a property of something else -> it's an ATTRIBUTE.
   - No, it's just describing behavior/access rules -> no new class at all.

The three-way bucket (class / attribute / no-class-at-all) is the actual skill here, not the noun-spotting itself. Nouns are cheap to find; deciding which bucket each one belongs in is where real design judgment happens.
Practical Mechanics — Running R1 through R12
R1 (register/update profile): "user" needs its own identity → new class User. Name, phone number, password are nouns too, but they don't need independent tracking → they become plain attributes of User. This is the method's first real lesson: not every noun is a class.
R2 (participate in expenses): "expense" clearly needs its own stored identity (amount, description, participants) → new class Expense.
R3 (participate in groups): "group" needs its own identity (name, members, admin) → new class Group.
R4 (adding an expense): introduces many nouns at once (group, users, paid, owed, description), but all of them are attributes of Expense and Group, which already exist. No new class yet, but "paid / owed" is flagged as needing real thought soon.
R5 (total owed amount): attribute, not a class, it's a computed property of User.
R6/R7 (viewing history): describe a query, not a class → these become Service methods later. This is explicitly the same shape already seen in BookMyShow's R9 ("list movies in a city"): not every requirement changes the class diagram.
R8 (access restriction) and R9 (group membership control): both are rules, not classes.
R10 (individual settlement, the Transaction trap): covered in detail below.
R11 (group settle-up) and R12 (minimize transactions): R11 is the same idea as R10, scoped to one group; R12 is pure algorithm, already fully solved in session 12. Neither adds a new class.
The Transaction Trap
R10 literally says the app should show "a list of transactions." Following the noun-spotting method mechanically, this looks like an obvious signal for a new Transaction class.
Stress-testing that conclusion reveals a real problem: if Transaction is its own class/table, holding "who pays whom, how much," then every future balance calculation has to check two sources of truth: the original Expense table, and this new Transaction table. Two sources of truth for the same underlying kind of fact (money moving between people) is exactly the kind of design smell that produces subtle, hard-to-find bugs later, one table gets updated and the other doesn't, and now balances disagree depending on which table a query happens to read.
The fix: a settlement is really just an expense that cancels another expense out. If A owes B ₹1000, instead of creating a Transaction row, create a dummy Expense where A "paid" ₹1000 and B "owed" ₹1000. It is not a real expense from a trip, it is a record of a debt being settled, but it reuses the exact same table and the exact same paid/owed structure Expense already needs anyway.
Telling real and dummy expenses apart later requires a type flag directly on Expense, formalized as an ExpenseType enum: NORMAL for real expenses, PAYMENT for settlement ones.
Net result: no new class for Transaction. The "list of transactions" a user sees on screen is a DTO, a temporary, computed-on-the-fly list handed back by a Service method, never stored as its own table.
CLASS DIAGRAM — first conclusion:
  User
  Group
  Expense

(NOT Transaction — settlements reuse Expense, via a type flag.)

Deep-Dive: The Discriminator Column / Single-Table Pattern

This section goes beyond the live script and is flagged here explicitly. The lecture arrives at the dummy-expense trick through live reasoning about one specific case, but never names the general schema-design pattern it's an instance of, a pattern that shows up constantly in real systems and is a very commonly probed interview topic in its own right.

What It Means

The dummy-expense trick is a specific case of a well-known relational modeling technique usually called the discriminator column pattern (also called single-table inheritance, in JPA/Hibernate terms, via the @Inheritance(strategy = InheritanceType.SINGLE_TABLE) and @DiscriminatorColumn annotations).
The general idea: when two (or more) kinds of "things" share almost all the same shape (same columns, same relationships) but differ in meaning or behavior, you have three real options:
Separate tables, one per kind. Cleanest conceptually, but forces every query that needs "all rows of either kind" to union across tables, and duplicates schema for shared columns.
A shared parent table plus per-kind child tables (class-table inheritance). Normalized, no duplicate columns, but every read of a full row requires a join across parent and child tables.
One shared table, with a discriminator/type column distinguishing the kinds (single-table inheritance). No joins needed to read a full row, trivially fast to query "all rows of either kind" together, but the table can accumulate columns that are only meaningful for one kind, and every row wastes a little space on columns it doesn't use.
The choice is fundamentally a tradeoff between query simplicity (favoring one shared table) and schema cleanliness (favoring separate tables or class-table inheritance).
Splitwise's Expense with an ExpenseType (NORMAL / PAYMENT) discriminator is option 3: real and dummy expenses share every single column (amount, description, participants via ExpenseUser), and the only thing that differs is meaning, so a discriminator column is the correct choice, not an oversight.

A Worked Example Beyond Splitwise

Consider a payments system that needs to track both CreditTransaction and DebitTransaction. Both need an amount, a timestamp, an account reference, and a status.
If they are modeled as two separate tables, computing "this account's full transaction history, in order" requires a UNION across both tables, and adding a new shared field means altering two tables in lockstep.
Modeled as one transactions table with a transaction_type discriminator column (CREDIT / DEBIT), the same query becomes a single, simple SELECT ... ORDER BY created_at, and every shared column lives in exactly one place.
This is the exact same shape as Expense's ExpenseType: two conceptually different row-kinds, identical structure, unified by one flag.

When Not to Use It

If the two kinds genuinely diverge in structure, say, one needs five extra columns the other never uses, a discriminator column starts filling a table with nullable, half-used columns, which is a real design smell in its own right. At that point class-table inheritance (a shared base table plus per-kind extension tables) is usually the better tradeoff, even though it costs a join.
Quiz Recap

Question: A hypothetical requirement, "users should be able to leave a comment on any expense" is run through the noun-spotting method. Does "comment" need its own class, or is it just an attribute?

Correct answer: B — it needs its own class, Comment, since a comment has its own identity (who wrote it, when) and one expense could reasonably have many comments over time, the same shape that justified giving Expense its own class instead of just adding fields to User.

Why the distractors are wrong:

A (a single String attribute on Expense) fails because it can only ever represent one comment, ever, for the whole life of the expense, which contradicts "users should be able to comment" (plural, ongoing).
C (no class at all, treating it as a behavior like R6/R7) misapplies that bucket, R6/R7 were about viewing existing data, not about storing new data. A comment is genuinely new data that needs to persist.
D (attaching it to User instead of Expense) confuses who authored a piece of data with where that data structurally belongs. A comment belongs to the expense it's attached to; the author is just one of its attributes.
Hidden Pitfalls
Treating every noun as automatically a class. The noun-spotting method's real value is the three-way bucket test (class / attribute / no class), not the act of spotting nouns itself; skipping the bucket test recreates exactly the "R1 attributes" mistake the lecture explicitly avoids.
Reaching for a new table the moment a new noun appears in a requirement. R10's "list of transactions" is the textbook trap: the tempting, mechanical answer (new Transaction class) creates two sources of truth for one kind of fact. Always stress-test a tempting new class against "does this actually need to be queried independently, or can an existing structure represent it with one extra flag?"
Using a discriminator column when the two kinds structurally diverge. If two row-kinds need substantially different columns, forcing them into one table produces a pile of nullable, half-used columns; that's a sign class-table inheritance or separate tables is the better tradeoff, even at the cost of a join.
SECTION 4 — Attributes per Class + the Paid/Owed Problem
What It Means
First-pass attributes were sketched directly:
User:
  id, name, phoneNumber, password

Expense:
  id, description, amount, createdAt
  paidBy  : Map<User, Integer>   <- problem
  hadToPay: Map<User, Integer>   <- same problem
  type    : ExpenseType (NORMAL / PAYMENT)

Group:
  id, name, admin (User)
  members : List<User>
  expenses: List<Expense>

paidBy: Map<User, Integer> and hadToPay: Map<User, Integer> directly on Expense recreate a shape already seen and fixed once before in this series: BookMyShow's pricing problem, where price was initially placed directly on ShowSeat, when it was really a property of the relationship between Show and SeatType, not a clean attribute of either side alone.
Here, "how much did this specific user pay/owe for this specific expense" is a property of the relationship between a User and an Expense, not a clean attribute of Expense alone.
Two concrete problems with a Map<User, Integer> sitting directly on a row: it isn't a native relational concept (a real database column can't natively store a map), and it makes a common query, "show me every expense a user has paid into", impossible to run efficiently, since the information is buried inside a serialized structure on someone else's row.
Practical Mechanics
The fix follows the exact same move used for BookMyShow's pricing: pull the relationship out into its own mapping class, one row per (expense, user, amount) combination.
New mapping class: ExpenseUser
  expense : Expense
  user    : User
  amount  : int
  type    : ExpenseUserType (PAID / HAD_TO_PAY)

A naming decision was locked in explicitly, because raw interview notes for this exact problem can describe it ambiguously as "two separate tables, one for paid-by, one for had-to-pay." The chosen design is one merged table, with a type field distinguishing the two rows, the same instinct as using one ShowSeat table with a status field instead of separate tables per state in BookMyShow:
The class is ExpenseUser.
The enum is ExpenseUserType (PAID / HAD_TO_PAY).
A second design decision: Group has both members: List<User> and expenses: List<Expense>. Whether Expense should also point back to Group was resolved by thinking about access patterns, not just structure: per R7 ("all expenses in a group"), the natural query direction is from Group outward, so List<Expense> conceptually belongs on Group, even though the foreign key will physically sit on Expense in the real schema (a detail deferred to next class's relationship-mapping work).
Quiz Recap

Question: A hypothetical requirement adds a "currency" field to both Expense and User. Applying the same reasoning used for paid/owed, should currency become its own class, or a plain attribute?

Correct answer: B — a plain attribute directly on Expense and on User. The test that mattered for paid/owed was never "is this a new noun," it was "is this value a property of the relationship between two entities, or a standalone property of one entity." Paid/owed genuinely depends on both which expense and which user; currency is just an independent fact about one Expense and, separately, an independent fact about one User.

Why the distractors are wrong:

A over-applies the mapping-class pattern to a case where it doesn't fit; there's no relationship between two entities being described here.
C wrongly treats currency as a display-only concern, but it's real data needed for correctness (converting or comparing amounts), not just rendering.
D repeats the exact Map<User, String> mistake that was just fixed for paid/owed, applying a relationship-mapping fix to a value that was never a relationship in the first place.
Hidden Pitfalls
Storing a relationship's data as a map on one side of the relationship. Map<User, Integer> directly on Expense looks convenient in code but has no clean relational representation and blocks efficient querying from the other direction (per-user history).
Splitting one logical concept into two separate tables unnecessarily. Treating "paid" and "owed" as two different tables, rather than one ExpenseUser table with a type flag, duplicates schema and complicates any query that needs both sides together.
Confusing "which side conceptually owns a list" with "which side holds the foreign key." Group conceptually owning expenses (driven by query direction) is a different decision from where the physical foreign key lives in the schema (on Expense); conflating the two is a common source of confusion when relationship annotations get added later.
SECTION 5 — Schema Design
What It Means
The standard conversion algorithm applies: every class becomes a table, every primitive becomes a column, every non-primitive relationship gets checked for cardinality.
Raw interview notes for this problem sometimes create two extra lookup tables purely for the two enums (ExpenseType, ExpenseUserType), each just an id + value pair. This is exactly the scenario BookMyShow's two-question enum-vs-lookup-table test was built for.
The two-question test, recalled from BookMyShow:
How likely is this set of values to change without a redeploy?
Is this set of values even the same for every "owner," or does each owner define its own?
Practical Mechanics
Applying both questions to ExpenseType (NORMAL/PAYMENT) and ExpenseUserType (PAID/HAD_TO_PAY):
Neither is likely to change without a redeploy; every expense in the system is structurally either real or a settlement, and every participant row is structurally either a payer or an ower. These are fixed, structural distinctions, not configurable business data.
Unlike BookMyShow's SeatType, where different theatres genuinely wanted different tier names, nobody "owns" a different version of NORMAL/PAYMENT or PAID/HAD_TO_PAY.
Both pass the test as plain enums, stored directly as a column, overriding the raw notes' seven-table version down to five tables:
FINAL SCHEMA — 5 tables (not 7):

Users
  id, name, phone, password, created_at, updated_at

Groups
  id, name, created_by_id (FK -> Users), created_at, updated_at

Group_Members                    <- Group <-> User is Many-to-Many
  group_id (FK), user_id (FK)

Expense
  id, description, amount, created_by_id (FK -> Users),
  group_id (FK -> Groups, nullable — R4: group OR direct users),
  expense_type   (enum column: NORMAL / PAYMENT)
  created_at, updated_at

Expense_Users                    <- the ExpenseUser mapping class
  id, expense_id (FK), user_id (FK), amount,
  expense_user_type (enum column: PAID / HAD_TO_PAY)
  created_at, updated_at

group_id on Expense is deliberately nullable, because R4 says an expense specifies either a group or individual users directly, so an expense between two friends with no group at all is completely valid and must be representable with a null group_id.
Quiz Recap

Question: A hypothetical requirement lets each group define its own custom expense categories (e.g., "Goa Trip" wants Flights/Hotel/Food; "Roommates" wants Rent/Groceries/Wifi). Applying the two-question test, enum or lookup table?

Correct answer: B — a lookup table. Different groups define genuinely different sets of values, which is exactly the second question ("same set for every owner?") failing, the same reasoning that made BookMyShow's SeatType a real entity rather than an enum once different theatres wanted different tier names.

Why the distractors are wrong:

A and C both ignore the "different owners, different sets" signal; a single shared Java enum can't hold two theatres' (or here, two groups') independently defined value sets at once, regardless of how short the text labels are.
D (free text, no structure) throws away the ability to cleanly query or group expenses by category, which is functionality clearly implied by wanting "categories" in the first place.
Hidden Pitfalls
Defaulting to a lookup table for every enum-shaped concept, "just in case." ExpenseType and ExpenseUserType both pass the two-question test as plain enums; reflexively normalizing them into tables adds two unnecessary joins to every query that touches expenses, for no real flexibility gained.
Forgetting to make a foreign key nullable when a requirement explicitly allows an optional relationship. group_id must be nullable because R4 explicitly allows expenses with no group; a non-nullable foreign key here would silently make a valid use case impossible to represent.
Applying the enum-vs-lookup-table test only from memory instead of re-deriving it against the current requirement. Each new "is this an enum or a table" decision needs both questions re-asked against the specific values in front of you; the pattern doesn't transfer automatically just because it looked similar to a past case.
SECTION 6 — Spinning Up the Spring Boot Project
What It Means
Recall from BookMyShow: the five dependencies picked in Spring Initializr were Spring Boot DevTools (auto-restart), Lombok (generates getters/setters), Spring Configuration Processor (avoids hardcoded config), Spring Data JPA (brings in JPA + Hibernate), and MySQL Driver (lets Hibernate talk to MySQL specifically), plus H2 Database.
Session 12 already confirmed Splitwise doesn't need to persist data between runs, which changes one dependency choice today.
Practical Mechanics
The MySQL Driver is swapped for H2, an in-memory database. H2 behaves like a real relational database, real tables, real SQL, real JPA/Hibernate underneath, for the entire duration of one run of the app, and then is gone the moment the app stops. This matches the no-cross-run-persistence requirement exactly, with zero extra setup.
A second deliberate difference from BookMyShow: spring-boot-starter-web is not added today. There is no HTTP layer this time; input comes from the command line, not a REST API. The words "Controller" and "Service" are still used for class names, purely to preserve the same separation-of-concerns structure used throughout the series, but without any @RestController or @PostMapping annotations. This is a deliberate, named difference, not an oversight.

Hidden Pitfalls
Adding spring-boot-starter-web by habit. Copying the BookMyShow dependency list wholesale would pull in an HTTP layer this project has no use for; the input channel here is deliberately the command line.
Assuming H2 requires extra configuration to behave like a real database. H2 gives real SQL and real JPA/Hibernate behavior with essentially no setup difference from MySQL at the code level; the only real change is the driver/dependency choice, not the modeling approach.
Forgetting H2's data doesn't survive a restart. This is the correct behavior for Splitwise per the requirements, but it would be a bug if this project actually needed persistence across runs; the choice must be re-justified per project, not applied by default.
SECTION 7 — Live Model Build: BaseModel, User, Group
What It Means
BaseModel is recalled directly from BookMyShow: id, createdAt, updatedAt, marked with @MappedSuperclass to tell JPA these are shared fields for subclasses, not a table of their own.
Lombok's @Getter/@Setter annotations were flagged back in BookMyShow's dependency list ("auto-generates getters/setters") but never explained mechanically until today.
Two classes today (User, Group) both hit the same reserved-SQL-keyword problem, requiring an explicit table name via @Entity(name = "...").
Practical Mechanics
package com.scaler.splitwise.models;

@Getter
@Setter
@MappedSuperclass
public class BaseModel {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private Date createdAt;
    private Date updatedAt;
}

No automatic auditing yet; createdAt/updatedAt are set manually wherever needed for now, with automatic timestamps deferred to next class.
Lombok's actual mechanism: @Getter/@Setter cause Lombok to scan every field in the class and generate real getter and setter methods at compile time, not through any runtime trick. Lombok plugs into the build process and generates actual Java methods into the compiled class before the code even runs. Adding a new field later (e.g., a password field on User) means Lombok automatically picks it up and generates its accessor methods too, with nothing to remember to add by hand.
package com.scaler.splitwise.models;

@Getter
@Setter
@Entity(name = "users")
public class User extends BaseModel {
    private String name;
    private String phoneNumber;
    private String password;
}

User needs @Entity(name = "users") instead of plain @Entity because user is a reserved SQL keyword in several databases (Postgres, notably), the same bug category already caught once in BookMyShow. Naming the table explicitly sidesteps the problem regardless of which database dialect ends up running underneath H2.
package com.scaler.splitwise.models;

@Getter
@Setter
@Entity(name = "userGroup")
public class Group extends BaseModel {
    private String name;
    private List<User> members;
    private List<Expense> expenses;
    private User createdBy;
}

Group needs @Entity(name = "userGroup") for the same reason: GROUP is a reserved SQL keyword, used in GROUP BY clauses.
members and expenses are deliberately left as bare fields today, with no relationship annotations (@ManyToMany, @ManyToOne, etc.); wiring those up properly is next class's dedicated segment.
Quiz Recap

Question: A teammate writes @Getter @Setter public class Payment { private int amount; }, with no explicit getter/setter methods written anywhere, then calls payment.getAmount() from another class. Does this compile?

Correct answer: B — yes. Lombok generates getAmount() (and setAmount()) at compile time based on the amount field, before the rest of the code is compiled against it, regardless of whether the class is an entity or extends anything.

Why the distractors are wrong:

A assumes Lombok requires visibly written source code for the method to exist, missing that it is a compile-time code generator that produces real bytecode-level methods without requiring the source text to be present.
C invents a dependency on BaseModel that doesn't exist; Lombok works on any plain class regardless of inheritance.
D wrongly ties Lombok's behavior to JPA's @Entity; Lombok and JPA are two completely unrelated libraries solving unrelated problems (code generation vs. object-relational mapping), and neither depends on the other.
Hidden Pitfalls
Treating Lombok as a runtime "magic" mechanism. It is a compile-time annotation processor; understanding this matters for debugging (the generated methods are real, inspectable bytecode, not reflection-based proxies) and for reasoning about build tool configuration.
Forgetting the reserved-keyword check on new entity names. user, group, and other common English words are frequently also SQL keywords; skipping an explicit @Entity(name = "...") on any of them risks a runtime SQL syntax error that only appears once the table is actually created or queried.
Adding relationship annotations too early, out of habit. Group.members and Group.expenses are deliberately left as plain fields today; adding @ManyToMany/@OneToMany prematurely, before the dedicated relationship segment next class, risks getting the ownership/mappedBy side wrong without the full context needed to reason about it correctly.
SECTION 8 — Taking Input via the Command Line
What It Means
The naive, first-draft version of main() handles reading input and dispatching it via a single, ever-growing if/else if chain, one branch per command.
Checked against the Single Responsibility Principle (SRP, established since Module 2), this naive main() is doing three separate jobs at once: knowing every command that exists, knowing how to parse each one's input format, and knowing how to execute each one. Every new command means editing the same giant, growing chain.
Practical Mechanics
main() {
    while (true) {
        String input = /* read from CLI */;

        if (input matches "create user ...") {
            // create user logic
        } else if (input matches "add expense ...") {
            // add expense logic
        } else if (input matches "settle up ...") {
            // settle up logic
        }
        // ... one more else-if per command, forever
    }
}

Step 1 of the fix: give every command a common shape via an interface.
interface Command {
    boolean matches(String input);   // "does this input belong to me?"
    void execute(String input);      // "run my own logic"
}

Each command (CreateUser, AddExpense, SettleUpUser) becomes its own class implementing Command, knowing only about itself: its own input format and its own execution logic.
This alone doesn't fully solve the problem: main() still needs to know about every Command class in existence to check each one's matches(). The responsibility has moved, not disappeared.
Step 2 of the fix: a CommandExecutor holds the full list of commands, so main() never has to know about individual commands at all.
class CommandExecutor {
    List<Command> commands;

    void execute(String input) {
        for (Command command : commands) {
            if (command.matches(input)) {
                command.execute(input);
                return;
            }
        }
    }
}

main() {
    CommandExecutor executor = ...;
    while (true) {
        String input = /* read from CLI */;
        executor.execute(input);
    }
}

Final architecture: Main -> CommandExecutor -> <<Command>> interface -> one class per real command. main() now knows nothing about individual commands; adding a hundredth command means writing one new class, with zero changes to main() or CommandExecutor.

Deep-Dive: The Command Design Pattern (GoF)

This section goes beyond the live script and is flagged here explicitly. The lecture arrives at this exact structure entirely through live SRP reasoning but never names it as a formal, interview-recognized design pattern.

What It Means

What was just built by hand is the Command pattern, one of the 23 classic design patterns catalogued by the Gang of Four (Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides) in Design Patterns: Elements of Reusable Object-Oriented Software (1994), categorized as a behavioral pattern.
Formal definition: the Command pattern encapsulates a request (an action to perform, plus whatever data it needs) as a standalone object, so that requests can be issued, queued, logged, undone, or dispatched generically, without the code issuing the request needing to know anything about how it's actually carried out.
The pattern's four standard roles, mapped onto Splitwise's own classes:
Command (the interface): Command, with matches() and execute().
Concrete Command (one implementation per action): CreateUser, AddExpense, SettleUpUser.
Invoker (holds and triggers commands without knowing their internals): CommandExecutor.
Client (creates and wires everything up): main().
The core value proposition is exactly what SRP reasoning uncovered organically: the invoker (CommandExecutor) is decoupled from the concrete actions it triggers. It only ever talks to the Command interface, never to CreateUser or AddExpense by name. This is what lets a hundredth command get added without touching CommandExecutor at all.

A Second Worked Example, Structurally Different from Splitwise

Consider a text editor's undo/redo system. Every user action (typing a character, deleting a selection, pasting text) is wrapped as a Command object implementing execute() and, crucially, undo().
The editor keeps a stack of executed commands. Pressing "undo" pops the most recent command and calls its undo() method, reverting exactly that action, whatever it was, without the editor's core code needing an if/else chain checking "was this a type or a delete or a paste?"
This is structurally different from Splitwise's use in one important way: Splitwise's commands don't need to be reversible (undo() isn't part of the interface here), it only needs matches() and execute(). The text editor case needs the pattern's full power, including the reversibility that Command's encapsulation makes possible in the first place. This confirms the reasoning generalizes: the pattern's core idea (wrap an action as an object, dispatch generically) holds regardless of whether reversibility is needed, and the interface simply grows or shrinks to fit what the invoker actually needs to do with each command.

Tradeoffs Against the Naive Alternative

The naive if/else if chain is simpler to read for a system with two or three commands that will never grow. For any system expected to add commands over time, the Command pattern's extra initial ceremony (one interface, one class per command) pays for itself the moment a second or third command needs adding, since none of the existing code needs to change.
A cost worth naming honestly: the Command pattern trades a small number of large files (one big main()) for a larger number of small files (one class per command). This is a net win for maintainability once a system has more than a handful of commands, but it does mean more files to navigate, which is a real, if minor, cost.
Quiz Recap

Question: A new command, LeaveGroup, needs adding, triggered by input like "u3 leaveGroup g1". Under the final Main -> CommandExecutor -> Command interface -> implementations architecture, which existing classes need to change?

Correct answer: C — neither main() nor CommandExecutor need to change. One new class implementing Command is written and registered with CommandExecutor's list; nothing else changes.

Why the distractors are wrong:

A and B both describe exactly the SRP violation the whole redesign fixed; if either were true, nothing would have been solved.
D is unnecessary: matches() and execute() are already generic enough to express any command's own logic internally, without the interface itself needing to grow per command.
Hidden Pitfalls
Letting the invoker check concrete command types directly. If CommandExecutor ever needs an instanceof CreateUser check, the decoupling the pattern exists to provide has already been broken; all dispatch must go through the Command interface only.
Forgetting matches() needs to handle ambiguity. If two commands' matches() could both return true for the same input, the iteration order of CommandExecutor's list silently determines behavior; input formats need to be unambiguous by design, not by accident of list ordering.
Assuming Command always needs undo(). The interface should only contain what the invoker actually needs; Splitwise's commands don't need reversibility, so forcing an unused undo() onto every concrete command adds ceremony with no payoff.
SECTION 9 — AI Corner: Generating the Homework Models
What It Means
Two real classes (Expense, ExpenseUser) plus two enums are left as homework, generated first via AI, then checked by hand against the design already built together.
This exercise is genuinely open-ended: different AI tools, and even the same tool run twice, can produce different results. There is no single scripted "correct" AI output to compare against.
Practical Mechanics
The shared prompt asked for four Java files: an Expense entity, an ExpenseUser entity, and two enums (ExpenseType, ExpenseUserType), using Lombok and extending BaseModel.
The standing four-point checklist applies here exactly as it does in every AI Corner across this series:
Does it match our contract?
Does it follow our conventions?
Does it handle edge cases?
Does it fit our real system's actual constraints?
The specific, well-documented failure mode most likely to appear: many AI tools will independently reinvent something like Map<User, Integer> paidBy and Map<User, Integer> hadToPay directly on Expense, because that is the generic, obvious way to model "who paid what" without knowing this class's own whiteboard history from Section 4. This is not a scripted certainty for every student's output, but it's a real, common pattern worth actively checking for.
If this pattern appears in a generated Expense class, the fix is to delete the Map fields entirely; that information already lives correctly inside ExpenseUser rows, exactly as decided in Section 4.
The underlying lesson generalizes across every AI Corner in this series: AI defaults to the generic, obvious version of a problem because it cannot see design reasoning that happened outside the prompt itself. The judgment call, checking generated code against decisions made earlier in your own specific design process, belongs to the engineer, not the tool.
A secondary check applies to ExpenseUser and the two enums: confirming the generated shape actually matches what was hand-built (expense, user, amount, expenseUserType; enum values PAID/HAD_TO_PAY and NORMAL/PAYMENT), keeping whatever already matches and hand-fixing whatever doesn't.
Hidden Pitfalls
Assuming AI output automatically respects design decisions made earlier in the same session, outside the prompt. AI only sees what's in its context window; a decision made on a whiteboard, or even earlier in the same conversation but not restated in the prompt, has no guaranteed effect on the output.
Treating one AI run's result as universally representative. Because this exercise is genuinely non-deterministic, judging "the AI Corner" by a single run's output (good or bad) misses the actual lesson, that the checking process matters regardless of what any one run happens to produce.
Copying generated code wholesale without re-running it against the four-point checklist. The tedious-but-well-specified nature of this homework (writing two entities and two enums) makes it tempting to accept AI output verbatim; skipping the contract/conventions/edge-cases/fit check here reintroduces exactly the Map<User, Integer> mistake the class spent real time fixing by hand.
Common Pitfalls Summary
1.  Treating every noun in a requirement as automatically a class.
    -> The real test is the three-way bucket: does it need its own
       identity and storage, is it just an attribute, or is it just
       a behavior/query? Skipping this test recreates the mistake
       the noun-spotting method exists to prevent.

2.  Reaching for a brand-new table the moment a new noun appears.
    -> R10's "list of transactions" looked like it needed a
       Transaction class; it didn't. Always check whether an
       existing structure plus one extra flag can represent the
       new concept before creating a new table.

3.  Using a discriminator column when the two row-kinds structurally
    diverge.
    -> If the kinds need substantially different columns, a shared
       table fills up with unused, nullable columns; class-table
       inheritance or separate tables becomes the better tradeoff.

4.  Storing a relationship's data as a map on one side of the
    relationship (e.g., Map<User, Integer> on Expense).
    -> Maps aren't a native relational concept, and this blocks
       efficient querying from the other direction. Pull it into
       its own mapping class instead.

5.  Splitting one logical relationship into two separate tables
    unnecessarily (e.g., separate "paid" and "owed" tables).
    -> One table with a type flag (ExpenseUserType: PAID /
       HAD_TO_PAY) avoids duplicated schema and simplifies queries
       that need both sides together.

6.  Defaulting every enum-shaped value to a lookup table "just in
    case."
    -> Apply both questions: will this set change without a
       redeploy, and is the set the same for every owner? If both
       answers are "no," it's a plain enum, not a table.

7.  Forgetting to make a foreign key nullable when a requirement
    explicitly allows an optional relationship.
    -> Expense.group_id must be nullable because R4 allows
       ungrouped, direct-user expenses.

8.  Adding a web starter dependency or relationship annotations out
    of habit, copied from a prior project.
    -> Splitwise has no HTTP layer (CLI input only) and defers
       relationship annotations to next class deliberately; each
       project's dependencies and annotation timing need their own
       justification, not autopilot copying.

9.  Treating Lombok as a runtime mechanism rather than a compile-time
    code generator.
    -> Lombok generates real getter/setter methods into compiled
       bytecode before the program runs; it has nothing to do with
       reflection or runtime proxying.

10. Skipping the reserved-SQL-keyword check on new entity names.
    -> "user" and "group" are both reserved keywords in some SQL
       dialects; always consider an explicit @Entity(name = "...")
       for common English words used as class names.

11. Letting an "invoker" class check concrete command types
    directly (breaking the Command pattern's decoupling).
    -> CommandExecutor must only ever call through the Command
       interface, never check "is this a CreateUser?" by hand.

12. Settling expenses one at a time, as they're created, instead of
    across the whole group at once.
    -> This throws away legitimate cancellations between two
       people and produces more transactions than necessary; net
       balances must be computed across every expense first.

13. Assuming AI-generated code automatically respects design
    decisions made earlier outside the prompt.
    -> AI only sees what's in its context window; always re-check
       generated code against the four-point checklist (contract,
       conventions, edge cases, real system fit).

Higher-Level Hidden Pitfalls:

Conflating "this passed the noun-spotting method" with "this design is correct." The method is a tool for generating candidate classes quickly; it doesn't replace stress-testing each candidate against the specific requirements, exactly as the Transaction trap demonstrates. A technique that speeds up idea generation is not the same as a technique that guarantees correctness.
Under-investing in naming/vocabulary precision during a design session. The lecture explicitly pauses to lock in ExpenseUser/ExpenseUserType naming, specifically because ambiguous raw notes ("two separate tables") could easily have led different team members to build incompatible versions of the same idea; skipping this step in a real team setting is a common, costly source of integration bugs.
Key Terminology
Term	Meaning in Simple Words
Noun-spotting method	A technique for finding classes by reading a written requirements doc and pulling out its nouns, then bucketing each one as a class, an attribute, or neither.
Dummy expense / settlement-as-expense trick	Representing a debt settlement as a normal-looking Expense row (with a type flag) instead of inventing a separate Transaction class, to avoid two sources of truth for the same kind of fact.
Discriminator column / single-table inheritance	A schema pattern where two or more conceptually different row-kinds share one table, distinguished by a type/discriminator column, instead of living in separate tables.
ExpenseUser	The mapping class recording one (expense, user, amount, PAID or HAD_TO_PAY) combination, replacing a Map<User, Integer> directly on Expense.
ExpenseType	Enum distinguishing a real (NORMAL) expense from a settlement (PAYMENT) one.
ExpenseUserType	Enum distinguishing whether one ExpenseUser row represents money a person PAID or money they HAD_TO_PAY.
Command pattern	A GoF behavioral design pattern that wraps a request/action as a standalone object, so an invoker can trigger it generically without knowing its internals.
Invoker	The role in the Command pattern that holds and triggers commands without knowing their concrete types; here, CommandExecutor.
CommandExecutor	The class holding the full list of Command implementations and dispatching input to whichever one matches.
H2	An in-memory relational database that behaves like a real SQL database for the life of one program run, then discards all data when the program stops.
Lombok compile-time annotation processing	The mechanism by which @Getter/@Setter cause Lombok to generate real getter/setter methods into compiled bytecode during the build, not at runtime.

Terms deliberately not redefined here because they're already covered in a named prior Post-Read: the six-step design framework and its interview variant, SOLID principles, the Repository/Service/Controller layering, DTOs, the Strategy pattern (Post-Reads 1-7); the full JPA/Hibernate/Spring Boot stack including @Entity, @Id, @GeneratedValue, @MappedSuperclass, Maven, Spring Initializr (Post-Reads 8-9); BookMyShow's Show/SeatType pricing correction and the original two-question enum-vs-lookup-table test (BookMyShow Post-Reads); and the greedy get/give settlement algorithm, the extra_amount formula, and NP-hardness of exact transaction minimization (session 12's own script, cross-referenced directly in Section 1 above since no numbered Post-Read 12 exists yet).

Frequently Asked Interview Questions

1. Why didn't you create a separate Transaction class for settlements, given the requirement explicitly says "list of transactions"?
Because a settlement and a real expense have the exact same shape: an amount, a description, and who paid vs. who owed. Creating a separate Transaction class would mean every future balance calculation needs to check two tables instead of one, which is a classic two-sources-of-truth bug risk. Instead, a settlement is modeled as a dummy Expense row with a type flag (ExpenseType.PAYMENT), reusing the exact same paid/owed structure. The "list of transactions" shown to a user is computed on the fly as a DTO, never stored as its own entity.

2. Walk me through why paidBy/hadToPay couldn't just be maps on the Expense class.
A Map<User, Integer> isn't a native relational concept; a database column can't natively store a map. More importantly, "how much did this user pay for this expense" is really a property of the relationship between a User and an Expense, not a clean attribute of Expense alone. Burying it in a map also makes a common query, "show all expenses a user has paid into", inefficient, since that data lives serialized inside someone else's row instead of being independently queryable. The fix is a dedicated mapping class, ExpenseUser, with one row per (expense, user, amount) combination.

3. When would you choose a discriminator column versus separate tables for two similar kinds of data?
When the two kinds share almost all the same columns and relationships, and differ only in meaning, a discriminator column (one shared table, a type flag) avoids duplicated schema and makes "query all rows of either kind" trivial. When the two kinds diverge structurally, one needing several columns the other never uses, separate tables or class-table inheritance (a shared base table plus per-kind extension tables) is the better tradeoff, even though it costs an extra join, because it avoids a table full of unused, nullable columns.

4. Explain the two-question test for deciding between an enum and a lookup table, with an example of each outcome.
Ask two questions: will this set of values change without a redeploy, and is the set the same for every "owner" in the system, or does each owner define its own? If both answers are "no," it's a plain enum; ExpenseType (NORMAL/PAYMENT) and ExpenseUserType (PAID/HAD_TO_PAY) both pass this way, since they're fixed, structural distinctions nobody customizes. If either answer is "yes" (the set is mutable, or different owners want different sets), it needs a lookup table; BookMyShow's SeatType failed this test because different theatres wanted different tier names.

5. What is the Command design pattern, and where did it show up in this session?
The Command pattern encapsulates a request as a standalone object, so an invoker can trigger it generically without knowing its concrete type. It has four roles: Command (interface), Concrete Command (one class per action), Invoker (holds and dispatches commands), and Client (wires everything up). In this session, it appeared as the fix for a naive, ever-growing if/else if chain in main(): each CLI action became its own class implementing a Command interface (matches()/execute()), and a CommandExecutor (the invoker) holds the list and dispatches to whichever command matches, without ever needing to know concrete command types.

6. What problem does the Command pattern actually solve, in SRP terms?
The naive version forces one function to know every command that exists, how to parse each one's format, and how to execute each one, three separate responsibilities piled onto one function, violating SRP. The Command pattern splits these apart: each concrete command knows its own parsing and execution, and the invoker knows only the generic interface. The payoff is that adding a new command means writing one new class, with zero changes to existing code, satisfying the open/closed principle as a side effect of fixing the SRP violation.

7. Why does Splitwise use H2 instead of MySQL for this project, and what would make you choose differently?
Splitwise's requirements explicitly state no data needs to persist across runs. H2 is an in-memory database that behaves like a real relational database (real SQL, real JPA/Hibernate) for the life of one run, then discards everything when the program stops, matching that requirement exactly with no extra setup. MySQL (or another persistent database) would be the right choice the moment any requirement needs data to survive a restart, which is exactly why BookMyShow, which does need durable persistence, used MySQL instead.

8. What does @Getter/@Setter from Lombok actually do, mechanically?
Lombok is a compile-time annotation processor. It scans a class's fields during the build and generates real getter and setter methods directly into the compiled output, before the program ever runs. It is not a runtime proxy or reflection-based mechanism; the generated methods are ordinary, inspectable methods on the class, generated automatically so they never have to be hand-written or kept in sync with field changes.

9. Why does User need @Entity(name = "users") instead of plain @Entity?
Because user (and USER) is a reserved SQL keyword in some databases, including Postgres. Using plain @Entity would let Hibernate default the table name to User, which can collide with the reserved keyword and cause SQL errors depending on the underlying database dialect. Explicitly naming the table (users) avoids the collision regardless of which database ends up running underneath.

10. Why is finding the true minimum number of settlement transactions NP-hard, and what do you do about it in practice?
Finding the exact minimum set of transactions that zeroes out every balance in a group is equivalent to a combinatorial optimization problem with no known polynomial-time solution; verifying a guess is easy, but finding the optimal answer requires effectively trying combinations. In practice, a greedy approach, repeatedly matching the largest current getter with the largest current giver and settling the smaller of the two amounts, gives a fast (
𝑂
(
𝑛
log
⁡
𝑛
)
), good-in-practice approximation with a provable upper bound of 
𝑛
−
1
 transactions, without guaranteeing the true minimum.

11. Your teammate's AI-generated Expense class includes Map<User, Integer> paidBy again, after your team already decided against that design. What do you do?
Recognize this as expected AI behavior, not a fluke: AI defaults to the generic, obvious version of a modeling problem because it has no visibility into design decisions made outside the prompt, like a whiteboard discussion. The fix is to delete the map fields and confirm that same information is already captured correctly by the ExpenseUser mapping class, then re-run the generated code through the four-point checklist (contract, conventions, edge cases, fit to the real system) before accepting it.

12. How would you decide whether a new field should live directly on an entity, or in its own mapping table?
Ask whether the value depends on exactly one entity, or on the combination of two entities together. If it depends on just one entity (like a User's preferred currency), it's a plain attribute. If it genuinely depends on a specific pairing (like how much a specific user paid toward a specific expense, or a price for a specific show and seat type), it belongs in its own mapping class with a row per pairing, not as a map or list buried inside one side of the relationship.

Self-Check Questions
In your own words, explain why R10's "list of transactions" doesn't require a new Transaction class, and what would go wrong if it did.
Trace through the extra_amount formula by hand for a person who appears in 3 expenses: paid ₹0/owed ₹200; paid ₹600/owed ₹200; paid ₹0/owed ₹150. What is their final balance, and do they pay or receive overall?
Write the Command interface and a skeleton LogoutUser class implementing it, following the same shape used for CreateUser in this session.
Compare the discriminator-column approach used for Expense/ExpenseType against a hypothetical two-separate-tables approach. Under what condition would you switch to the two-table approach instead?
A new requirement says each user can set a monthly spending limit per group. Apply the noun-spotting method: does this need a new class, or is it an attribute? Justify your bucket choice.
Explain why Group.expenses is considered to conceptually belong on Group, even though the foreign key will physically live on Expense in the schema.
Trace through what happens if CommandExecutor's commands list contains two Command implementations whose matches() methods can both return true for the same input string. What determines which one actually runs?
Apply the two-question enum-vs-lookup-table test to a hypothetical new requirement: "each user can pick a profile visibility level: Public, Friends-Only, or Private." Would you model this as an enum or a lookup table? Justify with both questions explicitly.
Explain, without looking back at the document, why Lombok's @Getter/@Setter is described as "compile-time" rather than "runtime," and why that distinction matters for debugging.
Write a short paragraph explaining, as if to an interviewer, why greedy get/give settlement doesn't guarantee the mathematically minimum number of transactions, but is still the right practical choice.
Compare today's noun-spotting class-diagram method against the "visualize the real-world object" method used for TicTacToe, Parking Lot, and BookMyShow. Under what interview conditions would you prefer one over the other?
A generated ExpenseUser class from an AI tool is missing the expenseUserType field entirely. Walk through which of the four standing checklist questions (contract, conventions, edge cases, fit to real system) this failure violates, and why.
Further Reading
Session 12 script (Design Splitwise) — covers the full derivation of the extra_amount formula, the sorted-chain solution, the greedy two-heap solution with its 
𝑂
(
𝑛
log
⁡
𝑛
)
 complexity, and the NP-hardness argument for exact transaction minimization, none of which is re-derived in depth in this document since it belongs entirely to session 12.
BookMyShow Post-Reads (design and code sessions) — cover the original Show/SeatType pricing correction (the direct precedent for today's ExpenseUser fix), the original two-question enum-vs-lookup-table test, the full JPA/Hibernate/Spring Boot primer (@Entity, @Id, @MappedSuperclass, Spring Initializr dependency choices), and the reserved-SQL-keyword naming fix, none of which is re-taught from scratch here.
Design Patterns: Elements of Reusable Object-Oriented Software (Gamma, Helm, Johnson, Vlissides, the "Gang of Four") — the canonical text defining the Command pattern along with all 23 classic GoF patterns; the primary reference for the formal Command pattern structure taught in this document's deep-dive.
Baeldung, "Command Design Pattern in Java" — a widely used, practical walkthrough of implementing the Command pattern in Java, useful for seeing additional worked examples (including undo/redo variants) beyond the two covered in this document.
Hibernate ORM official documentation, section on inheritance mapping strategies (SINGLE_TABLE, JOINED, TABLE_PER_CLASS) — the authoritative reference for the discriminator-column / single-table inheritance pattern discussed in this document's schema deep-dive, including exact annotation usage (@Inheritance, @DiscriminatorColumn).
Project Lombok official documentation — the primary reference for exactly how @Getter, @Setter, and other Lombok annotations behave as compile-time annotation processors, useful for going deeper than this document's summary of the mechanism.
Homework
1. Build Expense, ExpenseUser, ExpenseType, and ExpenseUserType
   yourself, using today's spec and Lombok conventions — don't just
   copy the AI Corner's fixed version. Bring your own attempt.

2. Add plain @Entity annotations to every model (reserved-keyword
   check included) — but do NOT add relationship annotations yet;
   that's next class's dedicated topic.

3. Stretch goal, not required: attempt a basic Command interface
   and a CommandExecutor skeleton on your own, using today's
   pseudocode. We'll build the full real version together next
   class regardless of how far you get.

4. Implement Register User end-to-end — Controller, Service,
   Repository, DTOs — same pattern as Region/Booking from
   BookMyShow. This one's yours to build fully on your own.

5. Push your progress to GitHub — branch name:
   splitwise-code-part1-complete

Last changed by 
 
Tushar Harsan·Follow
0
30
Add a comment
Published on  HackMD
