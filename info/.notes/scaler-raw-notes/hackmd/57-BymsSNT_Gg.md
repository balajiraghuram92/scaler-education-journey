Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/BymsSNT_Gg

Pre-Reads-Backend-LLD-11 — Machine Coding - 11: Code BookMyShow 3

Context
This is the final BookMyShow class. Today closes out the project as far as it goes together, rather than continuing it into a fourth session, and anything left unsolved by the end becomes self-directed homework, not a topic to revisit later.
The main remaining gap from R10/R11 gets closed: last session's soft-locked, SERIALIZABLE-protected booking still couldn't handle a seat abandoned mid-payment, so today adds a lazy expiry check that re-evaluates a stale BLOCKED seat the moment someone else tries to book it.
Real user accounts get built for the first time this module: signup, login, and properly salted password hashing, none of which existed before today.
The session continues the running discipline of catching real bugs live by reading code critically rather than trusting it because it compiles, this time with a wrong Spring stereotype annotation, an unassigned constructor field, and an inert auditing annotation missing its activation switch.
The closing message of the session is explicit: the specific tools (Spring, JPA, bcrypt) are not the real takeaway. The transferable habit, repeated across all three BookMyShow classes, is building the obvious version, finding exactly where it breaks, and fixing it with the smallest correct tool.

Overview
Segment | What is covered | Concepts in play
Recall of the race-condition fix | Confirming what last session solved: check-then-act races, why long transactions and synchronized both fail, and the soft-lock plus SERIALIZABLE fix proved with real threads | Concurrency recall
Finishing bookMovie with lazy expiry | Adding a check that treats a BLOCKED seat older than 15 minutes as available again, without proactively rewriting any row until someone actually re-evaluates it | Lazy evaluation, expiry-on-read
Reusing PriceCalculator as-is | Recognizing that an alternative cue-card implementation offers no benefit over last session's direct lookup, and confirming the call site's parameter order matches the declared method signature | Avoiding unnecessary rewrites, call-site verification
Wiring BookingController | Applying the established @RestController/@PostMapping/@RequestBody pattern to make booking a real callable endpoint, with an honest gap around generic exception handling | REST endpoint wiring
Building User signup and login | DTOs, a repository with a duplicate-email lookup, and a service layer, while catching two real bugs live: a repository wrongly annotated @Service, and a constructor parameter accepted but never assigned to its field | Layered construction, live bug-catching
BCrypt password hashing | Why plaintext and naive fixed hashing both fail, how a salt embedded directly inside the stored hash makes verification possible without ever decrypting anything, and why matches() is required instead of equals() | Salted hashing, non-deterministic encoding
Automatic timestamps via JPA auditing | Why @CreatedDate/@LastModifiedDate alone do nothing, and what @EntityListeners plus @EnableJpaAuditing actually activate | JPA auditing infrastructure
AI Corner: a parallel CRUD stack | Generating a full Controller/Service/Repository/DTO stack for a new entity (Theatre) and checking it against the exact validation convention already established by hand elsewhere in the codebase | Verifying AI output against a system's own established conventions

Why This Session Matters
Lazy expiry checking (re-evaluating a stale hold only when someone actually needs the resource) is a widely used real-world pattern precisely because it avoids running background jobs constantly, and this session is explicit that it is a complement to, not a replacement for, proactive sweeping. Knowing when a system needs both is a genuine design maturity signal.
A repository interface wrongly annotated @Service, or a constructor parameter accepted but never assigned to its field, are exactly the kind of realistic, easy-to-miss mistakes that pass a compiler and even run without crashing, only to fail silently or semantically later. Catching these by reading code carefully, rather than trusting that "it compiles" means "it works," is core code-review discipline.
Storing passwords in plaintext or with a naive fixed hash is one of the most common and most damaging real-world security failures. Understanding why a salt has to be different every time, and how it can be embedded directly in the stored value without ever needing to be decrypted, is foundational security knowledge expected of any backend engineer.
@CreatedDate/@LastModifiedDate silently doing nothing without @EnableJpaAuditing is the same "silent failure" shape seen earlier in this module with reserved SQL keywords and EnumType.ORDINAL. Recognizing this pattern, an annotation or configuration that looks correct but requires an easy-to-miss activation step, is a transferable debugging instinct.
The session's closing framing, that the real skill is building the obvious version, finding where it breaks, and fixing it with the smallest correct tool, is presented as the actual takeaway from the entire BookMyShow arc, not any one specific API. This is exactly the mindset expected in interviews when a candidate is asked to reason through a system live.

Real-World Use Cases
Lazy-expiry inventory holds: E-commerce checkouts and ticketing platforms commonly re-check whether a cart or seat hold has expired only at the moment another user's request needs that same resource, rather than running constant background sweeps, exactly the mechanism used for the seat-lock timeout here.
Layered CRUD stacks in admin panels: Internal admin tools for adding a new store location, warehouse, or branch typically follow the exact same Controller-Service-Repository-DTO shape used here for adding a new Theatre, since the pattern is mechanical and repeatable once established.
Bcrypt salted hashing in real authentication: Virtually every production authentication system (login flows for banking apps, SaaS products, e-commerce accounts) uses a salted, adaptive hash function like bcrypt specifically so that two users with the same password never produce the same stored hash.
JPA auditing for audit trails: Financial and healthcare systems that are legally required to track exactly when a record was created or last modified rely on the same auditing infrastructure built here, since manually setting timestamps in every service method is both tedious and error-prone at scale.
Validating foreign key references before use: A real order-management or booking service always checks that a referenced ID (a warehouse ID, a region ID, a customer ID) genuinely exists before building a relationship around it, exactly the convention enforced on the AI-generated Theatre service in this session.
AI-assisted CRUD scaffolding: Engineering teams commonly delegate mechanical, well-specified CRUD generation to AI tools for new entities, but always check the output against the team's own established conventions (validation patterns, exception handling, layering) rather than accepting it purely because it compiles and looks reasonable.

Connection to the Upcoming Class
The next session moves to a brand-new system, Splitwise, a genuinely different problem shape (expense-splitting and balance tracking rather than inventory and booking).
This session's own closing framing is the explicit bridge: the same underlying habits, building the obvious version first, identifying exactly where it breaks, and fixing it with the smallest correct tool, carry forward unchanged into Splitwise from day one. This connection is stated directly in today's script rather than being inferred.
The layered architecture discipline (Controller, Service, Repository, DTO), the JPA mapping reasoning, and the AI-verification checklist used throughout BookMyShow all remain the default working method for Splitwise, without needing to be re-taught.
Note: no Splitwise-specific content (its own requirements or class diagram) has been shared yet, so this section is written best-effort based on this session's own closing statement rather than confirmed Splitwise material.

Prerequisites from the Previous Class
The check-then-act race condition and why naive fixes fail: Two users racing to book the same seat is a check-then-act race; a long-held transaction across an entire payment flow is correct but unusable at scale, and Java's synchronized provides no protection across multiple servers and is wasteful even on one.
Soft locking and SERIALIZABLE isolation: A soft lock uses an existing status field (ShowSeatStatus.BLOCKED) rather than an actual database lock, keeping the real transaction short; SERIALIZABLE isolation is what actually detects and rejects a conflicting concurrent write.
The real concurrency test: The fix was proved using two genuinely separate threads targeting the same seats, checking that across repeated runs there is never zero successes and never two successes for the same seat pair.
BookingService's step-by-step plan: The nine-step plan (fetch user and show, lock the seats via check-then-block, create the booking) was established last session with only the locking mechanism finished; today's session fills in the remaining logic around that same plan, including price calculation via the existing PriceCalculator.
Established conventions carried forward: @RestController/@PostMapping/@RequestBody for real JSON endpoints, DTOs carrying IDs rather than full objects, and constructor injection with @Autowired are all reused directly without re-derivation today.

Key Concept Preview
A lazy expiry check does not rewrite a stale row the moment it becomes stale. The row can sit BLOCKED in the database for hours; it only gets re-evaluated the instant someone else's request actually reads it and reapplies the rule. This is why real systems often run a lazy check alongside an occasional background sweep, rather than relying on either alone.
Accepting a constructor parameter and never assigning it to the matching field is a bug that compiles cleanly and can even run without an immediate crash. The field simply stays null until something eventually calls a method that needs it, at which point the failure appears far from where the actual mistake was made.
A salted hash is not decrypted during login. The salt is embedded directly inside the stored hash string itself; verifying a password means re-extracting that same salt, re-hashing the login attempt with it, and comparing the result, never reversing anything.
An annotation like @CreatedDate is inert on its own. It requires both @EntityListeners(AuditingEntityListener.class) on the base class and @EnableJpaAuditing on the application's entry point before it does anything at all, the same "looks correct, silently does nothing" shape seen earlier with reserved keywords and EnumType.ORDINAL.

What You Will Walk Away With
Implement a lazy expiry check that treats a stale temporary hold as available again without proactively rewriting the database
Explain why a lazy expiry check and a scheduled background sweep are complementary, not redundant
Identify a repository interface with the wrong Spring stereotype annotation and correct it
Identify an accepted-but-unassigned constructor parameter and correct it, recognizing why the bug can pass a compiler unnoticed
Explain why passwords must be hashed with a salt that differs on every call, and why a naive fixed hash function is unsafe
Distinguish encode() from matches() for password verification, and explain how a stored hash embeds its own salt
Diagnose why an auditing annotation is producing null values, and correctly activate it with the required listener and application-level flag
Apply an established validation convention (verifying a foreign ID exists via findById().orElseThrow()) when checking AI-generated code for a new entity
Identify when reusing an existing, working implementation is preferable to an alternative AI-suggested rewrite with no real benefit
Articulate the transferable pattern behind this entire session and the BookMyShow arc: build the obvious version, find where it breaks, fix it with the smallest correct tool
