Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/Hy2Tk1yKMx

Pre-Reads : Machine Coding - 12: Design Splitwise

Context
This session moves to a brand-new system, Splitwise, roleplayed as a real machine coding interview at a company like CRED or Flipkart, start to finish, greeting through requirements through algorithm design.
Today marks a genuine structural departure from Parking Lot and BookMyShow: no class diagram gets built live. Splitwise's real hard problem is not structural, it is algorithmic, how to settle a group of people up using as few transactions as possible, and that problem earns most of today's time. Class diagram and schema design move to the start of Code Splitwise 1, using a new method (spotting nouns directly in the requirements doc), and this shift is called out openly rather than treated as a silent cut.
No Spring Boot or JPA primer is needed this time. That entire stack was already built across the three BookMyShow code sessions and gets reused, not retaught.
Requirements are numbered R1 through R12 for easy reference, kept visible on a dedicated board page throughout, the same discipline used for BookMyShow's R1-R18.
The persistence question, whether data needs to survive between runs, is answered directly from the requirements doc this time rather than left as an open design choice.

Overview
Segment | What is covered | Concepts in play
Framework recall and today's structure | Recalling the six-step framework, then naming the structural change: no live class diagram today, and why the algorithm deserves the time instead | Framework adaptation to a problem's real difficulty
The interview, roleplayed | Introducing Splitwise as an expense-tracking and expense-sharing application, and what "settle up" actually hands back to a user | Product framing before design
Steps in a machine coding interview | The six interview steps as framed by this session's cue card, including a new closing step, Follow-up | Interview structure literacy
Requirements R1 through R12 | Profile and group basics, the paid-vs-owed distinction and its sum invariant, visibility and access-control rules, individual settle-up (R10) versus group settle-up (R11), and the good-to-have transaction-minimization goal (R12) | Requirement decomposition, invariants, scope boundaries
Input format and the three clarifying questions | Confirming scope (entities only), persistence (none needed), and interaction mode (command line), using the same three questions asked in every design lecture | Clarifying-question discipline
Setting up the settle-up problem | Deriving the extra_amount formula that computes each person's true net balance across every expense, and why it must always sum to zero | Net balance computation, invariant-based validation
Solution 1: the sorted chain | A brute-force, mathematically correct approach using n-1 transactions, and its real practical weakness | Correctness versus real-world usability
Solution 2: the greedy get/give fix | Matching the biggest receiver with the biggest payer repeatedly, using two heaps, for a more sensible pairing at the same upper bound | Greedy algorithms, heap-based matching, NP-hard problem recognition
AI Corner: crowdsourced algorithm review | Everyone runs the same two prompts on their own AI tool, comparing genuinely different outputs live, both sanity-checking the greedy algorithm and diagnosing a flawed per-expense settlement idea | Verifying non-deterministic AI output as a live, collective exercise

Why This Session Matters
Distinguishing what someone paid from what they actually owed, and enforcing that the two sums always match, is a real data-integrity discipline. Any system tracking shared obligations (expense-splitting apps, cost-sharing platforms, joint billing systems) depends on this invariant holding, and a system that lets it drift silently loses money or trust.
Choosing to settle an entire group of transactions at once, rather than resolving each expense the moment it is created, is a recurring batch-versus-incremental tradeoff seen across real financial and logistics systems. Settling too eagerly throws away opportunities for cancellation and produces far more work than necessary.
Recognizing that minimizing transactions is NP-hard, and consciously choosing a fast, practical greedy approximation instead of chasing a guaranteed optimum, is exactly the kind of judgment call interviewers probe for. Knowing when to say "this is provably hard, here is a good-enough approach" is a mark of engineering maturity, not a shortcut to be embarrassed about.
The clarifying questions asked throughout this session (what happens when someone leaves a group, how does the app know a transaction really happened, does group membership alone affect a balance) are exactly the kind of active listening that separates a strong interview performance from one that jumps straight to drawing boxes.
Today's roleplay format itself is a rehearsal for the real thing: a genuine machine coding round runs two and a half to three hours, and practicing the full interview posture, greeting, clarifying, reasoning out loud, is as valuable as the content itself.

Real-World Use Cases
Expense-splitting ledgers: Applications like Splitwise, or shared-expense features inside banking apps, maintain a running ledger per group specifically so that "who owes whom" can be computed on demand rather than requiring money to change hands after every single expense.
Group access-control rules: Shared-workspace tools (a shared document, a shared calendar, a shared budget) commonly restrict visibility and membership changes to the creator or an admin, mirroring R9's rule that only a group's creator can add or remove members.
Batch settlement versus per-transaction settlement: Payment reconciliation systems and payroll systems typically batch obligations over a period and net them down before issuing payments, rather than settling every individual transaction the instant it occurs, for exactly the same reason today's session rejects per-expense settlement.
Greedy approximation algorithms: Logistics and scheduling systems facing NP-hard optimization problems (vehicle routing, job scheduling) commonly use greedy heuristics that give a fast, good-enough answer with a known worst-case bound, the same tradeoff made here with the get/give heap approach.
NP-hard problems accepted with practical approximations: Real production systems regularly encounter problems with no efficient exact solution and deliberately choose an approximation with understood limits, rather than either pretending an easy exact solution exists or refusing to ship anything.
AI-assisted algorithm review: Engineers reviewing a hand-designed algorithm often run it past an AI tool for a quick sanity check on edge cases (tie-breaking, rounding, termination conditions), while still deciding for themselves which flagged issues are real gaps versus non-issues, exactly the discipline modeled in today's AI Corner.

Connection to the Upcoming Class
Code Splitwise 1 builds the class diagram live using a method not used before in this module: spotting nouns directly in the written requirements doc, rather than reasoning through the physical-hierarchy style used for Parking Lot and BookMyShow.
That same session builds the schema and starts handling real command-line input, the two pieces explicitly deferred out of today's session.
The extra_amount formula and the greedy get/give algorithm designed today are the actual logic the next session's settlement service will need to implement in working code; today's reasoning is not theoretical, it is the direct blueprint for that implementation.
The homework for this session (guessing which requirements imply new classes) is explicitly designed to be compared against the noun-spotting method taught next class.

Prerequisites from the Previous Class
Layered architecture and DTO discipline: Controller, Service, and Repository layers, with DTOs carrying identifiers rather than full objects across a controller boundary, were fully established across the three BookMyShow code sessions and are assumed as the default working method going forward, including for Splitwise.
The AI-verification checklist: The same discipline of checking AI output against a system's own real contract, conventions, edge cases, and design decisions, used repeatedly across BookMyShow, reappears today in a new form: crowdsourced across the whole class rather than run once by the instructor.
Naming a hard problem before solving it: BookMyShow's seat-locking race condition was named clearly in one session and only resolved with real code two sessions later. Today's session applies the same discipline to transaction minimization: name it as NP-hard, then commit to a deliberately imperfect but practical fix.
Build the obvious version, find where it breaks, fix it with the smallest correct tool: This closing instinct from BookMyShow's wrap-up resurfaces directly today as brute-force-first: Solution 1 (the sorted chain) is built and proven correct before its real-world weakness motivates Solution 2 (the greedy fix).

Key Concept Preview
For any single expense, the total of what people paid must always equal the total of what people owed. This is not a stylistic preference, it is an invariant: if a system's numbers do not sum this way, money has silently vanished or appeared from nowhere.
Settling one expense at a time, the instant it is created, throws away the chance to cancel obligations against each other. A group's balances must be computed across every expense together before any settlement transactions are generated.
NP-hard does not mean unsolvable. It means no known algorithm can find the guaranteed exact best answer quickly for every case. The professional response is not to refuse to ship, it is to choose a fast, well-understood approximation and be explicit about what it does not guarantee.
The greedy get/give algorithm gives an upper bound of n-1 transactions, the same bound as the naive sorted-chain approach, but it does not promise the true mathematical minimum. In practice it often does better than the naive approach and produces far more sensible pairings, but "better in practice" and "provably optimal" are two different claims.
R10 (individual settle-up) and R11 (group settle-up) look similar but differ in scope: R10 settles one person across every expense they are part of anywhere, while R11 settles an entire group using only that group's own expenses, leaving a member's balances from unrelated contexts untouched.

What You Will Walk Away With
Distinguish "who paid" from "who owed" for a given expense, and validate an expense entry against the sum invariant
Explain why group membership and expense participation are separate concepts, and why leaving a group requires being settled first
Distinguish the scope of an individual settle-up (R10) from a group settle-up (R11)
Compute a person's true net balance (extra_amount) across multiple expenses, and verify that all balances in a group sum to zero
Explain why settling a group of expenses all at once produces better results than settling each expense individually
Trace the sorted-chain (brute-force) settlement approach by hand and identify its real practical weakness despite being mathematically correct
Trace the greedy get/give settlement approach by hand, including how ties in the get/give amounts are resolved
Justify why transaction minimization is treated as NP-hard, and explain what a greedy approximation does and does not guarantee
Reason about the time complexity of a heap-based greedy matching approach
Evaluate genuinely varied AI-generated feedback on a hand-designed algorithm, and decide independently which flagged issues are real gaps
