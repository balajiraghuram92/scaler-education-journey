Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/SyZCJ1kYfl

Post Read : Machine Coding - 12: Design Splitwise
Tushar Harsan·Follow
Last edited by
Tushar Harsan
on
Sep 9, 2026
POST-READ	Applied Design & Machine Coding	Machine Coding - 12: Design Splitwise
Introduction

Post-Read 11 closed out the three-lecture BookMyShow code arc: a race-safe booking flow, hashed passwords, and automatic timestamping, all reaching a genuinely complete state. This document opens a brand-new system, Splitwise, an expense-tracking and expense-sharing application, and it is a genuine milestone for a structural reason worth naming clearly: unlike Parking Lot and BookMyShow, the class diagram is not built live in this session.

Splitwise's real hard problem is not structural, it is algorithmic: given a group of people who owe each other money in a tangle of directions, how do you settle everyone up using as few transactions as possible? That question is rich enough to deserve most of this session's live time, so the class diagram and schema move to Code Splitwise 1, built there using a new method, spotting nouns directly inside a written requirements document.
No JPA or Spring Boot primer appears in this session. That entire stack was already built for BookMyShow across Post-Reads 9 through 11, and this project reuses it directly rather than re-deriving it.
Running examples carried through this document: the Goa-trip dinner-bill scenario used to derive the paid-versus-owed distinction, a four-person worked example carried through the entire settle-up derivation, and two competing settlement algorithms, a brute-force sorted chain and a practical greedy two-heap approach.
This session contains no 🎬 Animation blocks. Every visual referenced is a static diagram from the actual lecture material, and each one is embedded directly below, at the exact point where the lecture places it.
One clearly flagged addition beyond the live script appears in this document: a supplementary deep-dive explaining why minimizing transactions is provably NP-hard, a claim the live lecture states directly but does not derive. This sits right after Section 6, where the lecture itself first raises the claim.
This session's three quizzes (the paid-versus-owed sum check, the individual settle-up ledger, the greedy-round trace) and its two AI Corner touchpoints (one genuinely open-ended, one with a definite, fully-reasoned answer) are both folded in fully below.
Section 1: Opening, Framework Recall and Today's Structure
What It Means

Recalling the six-step framework already established in Post-Read 8: Overview → Gather Requirements → Clarify Requirements → Class Diagram → Schema Diagram → Working Code. This session's own material frames these steps slightly differently: Overview, Clarify Requirements, Class Diagram, Schema Design, Code, and one genuinely new addition, Follow-up, at the end.

A structural note worth stating plainly, not glossing over: unlike Parking Lot and BookMyShow, the class diagram is not built live today. Splitwise's real hard problem is an algorithm, settling a group of people up using as few transactions as possible, and that deserves real live time. Class diagram and schema get built live in Code Splitwise 1, using a method not yet used in this course: spotting nouns directly in a written requirements document.

No persistence question needs speculation today either, this gets answered directly from the requirements document itself in Section 4, with no need to guess how next session's code will satisfy it alongside JPA.

Hidden Pitfalls
Expecting today's session to end with a completed class diagram, the way every prior Design lecture has: this is a deliberate structural change, named explicitly, not an oversight or a silent cut; the algorithm genuinely needed the time instead.
Treating the "Follow-up" step as optional interview theater: it is the step where an interviewer probes how deep a candidate's thinking actually goes once a working solution exists ("what if a group has 500 members?"), and it is worth taking as seriously as any other step in the framework.
Section 2: The Interview, Roleplayed, Meeting Splitwise
What It Means

This session runs as a roleplayed interview at a company like CRED or Flipkart, start to finish, greeting, requirements, clarifying questions, the works. A real machine coding round like this usually runs 2.5 to 3 hours.

Splitwise, in plain terms:

It is an expense-tracking and expense-sharing application.
It lets a group note down who paid, how much, and who was involved.
It tracks running balances as more expenses get added over time.
At the end, when someone hits settle up, it tells that person exactly who owes what to whom.
Every user is assumed to have the app on their phone, throughout this entire exercise.

A preview of exactly what "settle up" hands back to a user, worth keeping in view for the rest of this document: not a single number, but a concrete list of transactions to actually make.

The interviewer's framing for today's problem: a set of requirements gets handed over, and the candidate is expected to first describe how they'd design the system, the class diagram, and then implement it: classes, tables, code.

Hidden Pitfalls
Skipping the "what is this system" framing before diving into requirements: aligning on the one-line mental model (expense tracking plus sharing, settle-up reveals who owes whom) first is what makes every requirement that follows easier to interpret correctly.
Section 3: Steps in a Machine Coding Interview
What It Means
1. Overview             — what IS this system, in one paragraph
2. Clarify Requirements — ask questions, don't assume
3. Class Diagram        — (live next class, not today)
4. Schema Design        — (live next class, not today)
5. Code
6. Follow-up            — interviewer pushes on edge cases / scale,
                           after your code already works

The Overview is essentially what Section 2 already accomplished. Clarifying questions should always be asked out loud in a real interview, interviewers want to see this reasoning happen visibly, not skipped in favor of jumping straight to drawing boxes. Follow-up is genuinely new to this course as a named step: it is what an interviewer asks after a solution already works, to see how deep the candidate's thinking goes, for example, "what if a group has 500 members?"

Hidden Pitfalls
Treating clarifying questions as a formality to rush through: interviewers specifically evaluate whether a candidate asks good questions before designing; visibly reasoning through ambiguity is part of what's being assessed, not friction to minimize.
Section 4: Requirements, R1 to R12
What It Means

Requirements arrive in document form in a real interview, not spoken piecemeal. They are walked through here strictly in order, R1 through R12.

R1 and R2, Quick Facts
R1: Users can register and update their profiles. A profile must
    contain at least name, phone number, and password.
R2: Users can participate in expenses with other users.

R1 establishes the attributes of a User class. R2 is just a use-case statement for now, R4 gives it real shape. Nothing to debate on either.

R3, Groups
R3: Users can participate in groups.

This is exactly the kind of vague line worth pushing back on in a real interview. A reasonable clarifying question here: "Can you explain a bit more about how the group is going to work?"

Imagine a few friends going on a Goa trip together.
Instead of manually adding each person to every single payment, a group gets created, "Goa Trip," and a link gets shared.
Anyone in the group can see any expense logged in that group.
But being in the group does not automatically mean being part of every expense, a group member might see an expense they weren't involved in at all.

That last point, "can see, but may not be part of," resurfaces explicitly again in R4.

R4, Adding an Expense
R4: To add an expense, a user must specify either the group or the
    other users involved, along with who paid what and who owes
    what, plus a description.

This is genuinely the richest requirement in the whole list.

A question worth asking directly: who should be allowed to see one specific expense once it's logged? Only the participants of that specific expense, not the whole group by default, the flip side of what was just noted in R3.

The real substance of R4: who paid what versus who owes what are two genuinely different things, and an interviewer will not spell out the difference. It has to be interpreted.

Three friends go for dinner. Total bill: ₹3000.

WHO PAID (actual money handed over):
   A paid ₹3000   (A used their card for the whole bill)
   B paid ₹0
   C paid ₹0

WHO OWES (their fair share of the ₹3000):
   Initial idea — split equally:
   A owes ₹1000   B owes ₹1000   C owes ₹1000

Complicating this slightly, the real interview trap:

Turns out B is non-vegetarian and ordered much more of the bill.
The group agrees a fair split isn't equal anymore:

   A owes ₹800
   B owes ₹1400
   C owes ₹800
   ------------------
   Total owed: ₹3000   (matches total paid)

A question worth answering directly: whatever numbers get used for "who owes what," what must always be true, no matter how the split is decided? The sum of "who paid" must always equal the sum of "who owes," both must equal the total expense amount. This invariant, 
∑
paid
=
∑
owed
=
total
, gets reused when balances are computed across multiple expenses in Section 6, and it's a genuinely useful sanity check to build into any real implementation later.

Quiz Recap

A ₹4000 dinner expense is logged with: A paid ₹4000, B paid ₹0, C paid ₹0. The split entered is: A owes ₹1500, B owes ₹1500, C owes ₹500. Is this a valid expense entry?

A) Yes, every person has a non-negative owed amount, so it's fine
B) No, 1500 + 1500 + 500 = 3500, which doesn't equal the ₹4000 that was actually paid
C) No, A can't both pay and owe money for the same expense
D) Yes, as long as A (who paid) owes ₹0
Correct answer: B. The rule just derived is that 
∑
owed
=
∑
paid
=
total
. Here the owed amounts sum to 3500, not 4000, so ₹500 has vanished, a real data-integrity bug this system should reject.
Why A is wrong: "non-negative" is not the actual rule being tested; "sums match" is. Every value here is non-negative, and the entry is still invalid.
Why C is wrong: A paying the bill and still owing their fair share is completely normal, it is in fact the exact example just built above with the ₹3000 dinner.
Why D is wrong: it invents a rule that doesn't exist; nothing says the payer must owe ₹0, the payer simply gets credited for the money they physically handed over.
R5, R6, R7, R8, Quick Facts
R5: A user can see their total owed amount.
R6: A user can see a history of the expenses they're involved in.
R7: A user can see a history of the expenses made in a group
    they're participating in.
R8: Users shouldn't be able to query about groups they are not a
    member of.

R5 is one single net number on a dashboard, right now.
R6 is a full personal history, the individual expenses that fed into that number.
R7 is the same idea, scoped to one group instead of a user's whole life.
R8 is a straightforward access-control rule.

A clarifying question worth asking about R6/R7, tying directly back to R3: if an expense belongs to a group, does a group member see it in their history even if they weren't personally a participant in that expense? Raising this out loud in an interview is good instinct, it demonstrates active listening rather than passive nodding.

R9, Group Membership Control
R9: Only the user who created a group can add or remove members.

A genuinely good clarifying question here concerns what happens on the way out of a group: "If a person leaves the group, does their expense history get removed too?"

The actual rule: a person cannot leave a group while they're still part of any expense in that group. They can leave only after they're fully settled up within that group, which is exactly why group settle-up (R11) exists.

R10, Individual Settlement
R10: Users can request a settlement. The application should show
     a list of transactions, which when executed will ensure that
     the user no longer owes or receives money from any other
     user. Note that this need not settle up any other users.

Unpacking this slowly, it's dense:

"Settle up" for ONE user, say A:
- App shows a LIST of transactions (not just one).
- Each transaction: [who] -> [pays] -> [A or A pays them]
- Executing ALL of them brings A's own net balance to exactly 0.
- Everyone ELSE's balance may still be non-zero. Not our problem
  for THIS user's settle-up request.

A real question a candidate should ask here: how does the app actually know a transaction really happened? Splitwise doesn't move real money. There must be some manual confirmation, a checkbox or tick the user presses. There's a tick per transaction, the user marks it done manually, and the moment it's ticked, that specific transaction updates the balance.

One subtlety worth stating directly: after doing this, the requesting user is settled, but the other party in that transaction isn't necessarily settled overall, they might have other pending transactions entirely unrelated to this one. Also worth noting: simply adding someone to a group changes nothing about their balance, only actually being part of a payment does. One more detail buried in this requirement: expenses can be updated after creation, and when that happens, everyone involved gets notified and everyone's balance recalculates. Finally, multiple currencies are deliberately ignored, one currency only, for this whole exercise.

Quiz Recap

User A requests an individual settle-up. The app shows: "B owes you ₹500" and "you owe C ₹200." A ticks off "B owes you ₹500" as done, but hasn't yet done anything about the ₹200 to C. What is A's state right now?

A) A is fully settled, since they initiated the settle-up request
B) A still owes C ₹200, only the ticked transaction updates the balance; the untouched one is still pending
C) Both transactions auto-complete the moment settle-up is requested
D) B is now also fully settled with everyone, since their transaction with A is done
Correct answer: B. R10 is explicit that a settle-up shows a list of transactions, and each one only updates the balance once it's individually marked done. Initiating the request itself doesn't auto-complete anything.
Why A is wrong: requesting a settle-up only reveals the list; it does not execute anything on its own.
Why C is wrong: it invents an auto-complete behavior that isn't part of the requirement; each transaction requires its own individual confirmation.
Why D is wrong: it confuses "B is settled with A" with "B is settled with everyone"; B might still owe or be owed money by other people entirely, unrelated to this one transaction with A.
R11, Group Settle-Up
R11: Users can request a settle-up for any group they're
     participating in. The application should show a list of
     transactions which, if executed, will ensure everyone
     participating in the group is settled up (nets to 0).
     Only expenses inside that group are considered — expenses
     outside the group are untouched.

The genuine difference from R10: R10 settles just one person, across everything they owe anywhere. R11 settles an entire group, but only using that group's own expenses, a person's balance from a completely separate trip is untouched. Two different scopes, not to be conflated.

R12, Minimize Transactions (Good-to-Have)
R12: When settling a group, minimize the number of transactions
     members need to make.

Marked explicitly as "good to have," worth flagging that exact distinction to an interviewer. Splitwise isn't a legal or accounting app, it simplifies real life. There are always multiple valid ways to settle a group up; the goal is the one with the fewest transactions, though without formally guaranteeing it is the mathematical minimum.

A small hint worth noting directly: this is secretly a real algorithms problem hiding inside a design interview. Here's a taste of exactly that, the same group of four settled two different ways:

Hidden Pitfalls
Treating R3's "participate in groups" as meaning every group member automatically shares in every expense: R4 explicitly contradicts this; only the specific participants of an expense see and owe for it, membership alone confers only visibility, not automatic participation.
Assuming a settled requirement means the individual initiating settle-up is the only one affected: R10 explicitly limits the scope to the requesting user's own balance; other parties in those same transactions may still have unrelated pending balances.
Conflating R10's and R11's scope: R10 settles one person across everything, everywhere; R11 settles an entire group using only that group's expenses. Applying the wrong scope produces incorrect settlement lists.
Treating R12 as a hard, guaranteed requirement rather than a "good to have": it is explicitly marked as good-to-have, and this distinction matters for how an interviewer should be told the true minimum is not being formally guaranteed.
Section 5: Input Format and Recalling the Three Clarifying Questions
What It Means

Before touching the algorithm, it's worth settling how input actually arrives.

This course has asked three standard clarifying questions in every design lecture so far:

Full system, or just the entities?
Persist data, or keep it in memory?
How does the user actually interact with this?

Today's answers, straight from what's already been stated, no digging required:

Just the entities and core logic, no need to build a full BookMyShow-style REST API today.
No persistence needed across runs, the interviewer already stated this plainly, back in Section 4.
Through the command line, plain CLI input, as shown above. This code isn't written today, that's Code Splitwise 1's job.

One real question posed by the interviewer at this point: "Given N expenses have already happened in a group, and someone clicks 'settle up,' how would you actually compute who pays whom, and how much?" The real question buried inside that: do transactions get settled one at a time as they happen, or does everything wait and get settled as a whole batch at "settle up" time?

Hidden Pitfalls
Assuming input format decisions belong in the class diagram: CLI versus REST is an interface concern, entirely separate from what classes and relationships need to exist; conflating the two adds unnecessary complexity to the wrong step.
Section 6: How to Settle Up, Setting Up the Real Problem
What It Means

The whole group of transactions has to be settled up at once, never just one in isolation. Processing expenses one at a time as they happen generates far more transactions than necessary. The full picture is needed first.

Three real sub-problems hiding inside "settle up":

How is it calculated who has to pay, and who has to receive, and how much?
Once that's known, from whom to whom should money actually flow?
Can this be done in the minimum number of transactions?

Every expense, underneath, is really just two lists:

Expense:
  whoPaid            : [ (person, amount), (person, amount), ... ]
  whoHadToPay (owed)  : [ (person, amount), (person, amount), ... ]

For any single, correctly-entered expense, the total of whoPaid and the total of whoHadToPay must be equal, the same invariant already established back in R4.

Computing each person's real final state across multiple expenses:

Practical Mechanics: The extra_amount Formula
for every person:
    extra_amount = 0

for every expense:
    extra_amount += whoPaid[person]        // money they put in
    extra_amount -= whoHadToPay[person]    // money that was really theirs to pay

More formally, for any person 
𝑝
, summed across every expense 
𝑒
 they appear in:

extra\_amount
(
𝑝
)
=
∑
𝑒
(
paid
𝑒
(
𝑝
)
−
owed
𝑒
(
𝑝
)
)

Computing this by hand for person A, across the four expenses in the image above:

Expense 1: A paid ₹1000, A owed ₹500   → +1000 - 500 = +500
Expense 2: A paid ₹3000, A owed ₹1000  → +3000 - 1000 = +2000
Expense 3: A paid ₹0,    A owed ₹500   → +0 - 500 = -500
Expense 4: A paid ₹0,    A owed ₹250   → +0 - 250 = -250
                                          -----------------
A's final extra_amount:                  +1750

A positive number means A is owed money overall, A put in more than their fair share across everything. A must receive ₹1750.

Quiz Recap

A different person, P, appears in 3 expenses: Expense 1, P paid ₹0, P owed ₹300. Expense 2, P paid ₹900, P owed ₹300. Expense 3, P paid ₹0, P owed ₹100. What is P's final extra_amount, and does that mean P pays or receives money overall?

A) +200, P receives ₹200 overall
B) −200, P has to pay ₹200 overall
C) +1300, P receives ₹1300, since that's the sum of all the "owed" amounts
D) +900, P receives ₹900, since that's the only expense P actually paid money in
Correct answer: A. Applying the formula exactly as done for person A above: Expense 1: 
0
−
300
=
−
300
. Expense 2: 
900
−
300
=
+
600
. Expense 3: 
0
−
100
=
−
100
. Sum: 
−
300
+
600
−
100
=
+
200
. Positive means P receives.
Why B is wrong: it has the right process but the wrong sign, a common slip when doing the subtraction mentally rather than term by term.
Why C is wrong: it mistakenly sums only the "owed" column instead of computing paid-minus-owed per expense before summing.
Why D is wrong: it wrongly assumes only expenses where the person personally paid money count toward their balance; every expense a person is listed in, whether or not they physically paid, affects their final balance.

Applying this to everyone in the real group example gives the full final picture:

A question worth answering directly: why must this sum always be exactly zero, no matter how many expenses or people are involved? Because for every single expense, 
∑
paid
=
∑
owed
, established back in R4. Adding up that invariant across every expense, for every person, can only ever net to zero overall. If a real implementation's final sum isn't zero, there's a bug somewhere in the input or the calculation, a genuinely useful sanity check to build in.

Sub-problem 1 (who pays or receives, and how much) is now solved. Sub-problems 2 and 3, from whom to whom, and minimizing transactions, remain.

Both bad news and good news arrive together here: minimizing the number of transactions is an NP-hard problem, no known polynomial-time solution exists. The only way to guarantee the true minimum is to try every possible combination of transactions. This won't be done, a greedy approach gets used instead: fast, and good in practice, even without a guaranteed-minimum promise.

Hidden Pitfalls
Settling expenses one at a time as they're created: this generates far more transactions than necessary; the full set of net balances across every expense in the group must be computed first before any settlement transactions are decided.
Forgetting that the sum of every person's extra_amount must equal zero: any nonzero final sum indicates a bug in the input data or the calculation itself, this is a genuine correctness invariant, not just a coincidence of the worked examples.
Confusing "NP-hard" with "impossible" or "impractically slow in every case": NP-hard means no known algorithm guarantees the exact optimal answer quickly for every possible input; it does not mean a good, fast, practical approximation is unavailable, exactly what the greedy approach in Section 8 provides.
Deep-Dive Beyond the Live Script: Why Minimizing Transactions Is Actually NP-Hard

This section goes beyond a straight transcription of the live class. The lecture itself states directly that minimizing transactions is NP-hard, but never actually shows why. Since understanding why a claim is true is genuinely more valuable than simply memorizing that it's true, this deep-dive works through the intuition behind that claim.

What It Means
Recall the greedy algorithm's real limitation from Section 6: it produces at most 
𝑛
−
1
 transactions for 
𝑛
 people, but the true minimum could sometimes be far fewer, if the group's balances happen to split up neatly.
The key insight connecting this to a known hard problem: any group of people whose balances sum to zero can potentially be broken into multiple independent sub-groups, each of which, on its own, also sums to zero. If a sub-group of 
𝑘
 people has balances summing to exactly zero, that sub-group can be settled entirely on its own, using at most 
𝑘
−
1
 transactions, completely independent of everyone else in the larger group.
The fewer transactions a settlement needs overall, the more such independent zero-sum sub-groups exist within the full group. Concretely: if a group of 
𝑛
 people can be split into 
𝑚
 independent zero-sum sub-groups, the total transactions needed is at most 
𝑛
−
𝑚
 (rather than 
𝑛
−
1
 for the whole group treated as one block).
So minimizing the total number of transactions is mathematically equivalent to a different question: what is the maximum number of independent zero-sum sub-groups this set of balances can be split into?
The Connection to a Classic Hard Problem
Finding out whether any non-trivial subset of a group's balances sums to exactly zero is, by itself, a version of a well-known problem in computer science called the Subset Sum problem: given a set of numbers, does some subset of them add up to a target value (here, zero)?
Subset Sum is known to be NP-complete in general (a close cousin of NP-hard), which means no algorithm is known that solves it quickly for every possible input as the numbers involved grow.
Finding the maximum number of ways to partition a whole set into multiple zero-sum groups (not just checking whether one such subset exists) is at least as hard as finding a single one, since checking every possible way to split the group into pieces, and checking each piece's sum, involves combinatorially many possibilities, options grow roughly as 
2
𝑛
 for a group of 
𝑛
 people.
This is why no algorithm is known that finds the provably optimal minimum number of transactions quickly for a large group; doing so would require efficiently solving a problem that is, in the worst case, exactly as hard as Subset Sum.
A Small Worked Illustration

Consider four people with balances 
+
300
,
−
100
,
−
100
,
−
100
.

Treated as one block (the greedy or chain approach), settling this takes up to 
4
−
1
=
3
 transactions.
But notice: the three negative balances (
−
100
,
−
100
,
−
100
) plus the one positive balance (
+
300
) can potentially be handled more cleverly if a smaller zero-sum subgroup exists elsewhere in a larger real-world example. In this specific small example, there is only one connected group (everyone owes the same person), so 3 transactions is actually necessary here, one payment from each debtor to the creditor.
The interesting case arises with more people: suppose an 8-person group's balances happen to split into two completely independent 4-person zero-sum clusters (two totally separate mini-settlements hiding inside one big group). Detecting that hidden structure, and thus settling the whole group of 8 in 
3
+
3
=
6
 transactions instead of a possible worse pairing, requires recognizing that split, and recognizing it in general, for an arbitrary set of balances, is exactly the computationally hard part.
Hidden Pitfalls
Assuming the greedy algorithm always finds the mathematically optimal number of transactions: it does not, and cannot, in general; it finds a good, fast, practical answer bounded by 
𝑛
−
1
, not a provably minimal one. The two can coincide in many everyday cases, but nothing guarantees it.
Assuming NP-hard problems have no reasonable solution at all: NP-hardness only rules out a guaranteed-fast method for the exact optimal answer on every input; fast, good-enough approximations (like the greedy approach in Section 8) remain entirely valid engineering choices, and are exactly what real systems use in practice.
Confusing "checking whether a zero-sum subset exists" with "finding the single best split of the whole group": the first question alone is already a known hard problem (Subset Sum); the second, needed for true transaction minimization, is at least as hard, since it implicitly requires answering many instances of the first.
Section 7: Solution 1, The Brute-Force Chain
What It Means

Building the simplest possible correct solution first, and seeing exactly what's wrong with it in practice. Sorting everyone by their final balance:

Algorithm:
  Walk the sorted list, left to right: A, B, C, D, ...
  At each step, person[i] settles fully with person[i+1]:
     - if person[i] needs to RECEIVE money, person[i+1] pays them
       exactly enough to bring person[i] to zero.
     - if person[i] needs to PAY money, person[i] pays person[i+1]
       exactly enough to bring person[i] to zero.
  Move to i+1, repeat.

In plain words: A tells B, "give me exactly the amount I need to be fully settled, then go collect the rest of what you're owed from whoever's next in line." B does the same to C, C to D, and so on down the chain.

A question worth answering directly: if there are 
𝑛
 people in the group, how many transactions does this always take? Exactly 
𝑛
−
1
, one settling handshake per adjacent pair in the sorted line.

This algorithm is mathematically correct, everyone ends up at exactly zero. So why might real users still be unhappy with it? The pairing is completely arbitrary, based only on sort order, not on who actually owed whom in real life. Someone might be forced to pay a total stranger in the group, someone they never personally transacted with, purely because of where they landed in the sorted list. It is mathematically fine but socially and practically awkward, "technically correct, but practically not user-friendly." That gap is exactly what Solution 2 closes.

Quiz Recap

A group of 5 people settles up using the Solution 1 chain approach. Person C, in the middle of the sorted list, never personally shared an expense with person E in real life. Under this algorithm, is it possible C ends up owing money directly to E?

A) No, the algorithm only creates transactions between people who actually shared a real expense together
B) Yes, the chain only cares about sorted position, not real history between people, so C could easily end up paired with someone they never actually transacted with
C) No, Solution 1 guarantees the minimum number of transactions, so it would never create an "unnecessary" pairing like this
D) Only if C and E are adjacent in the final sorted list, otherwise it's impossible
Correct answer: B. This is exactly the practical weakness just named. The chain algorithm settles people purely by sorted position, with zero awareness of real relationships between them.
Why A is wrong: it wrongly assumes the algorithm is relationship-aware; it isn't, it only knows sorted numerical position.
Why C is wrong: it wrongly assumes correctness implies user-friendliness; they are separate concerns entirely, which is the whole point of this section.
Why D is wrong: this is a trap; C and E don't need to be adjacent for a connection to form. Money "flows through" the chain, so a person can easily end up settling, indirectly, with someone far down the sorted list too, since each handshake only cares about the running remainder, not the original identities.
Hidden Pitfalls
Assuming mathematical correctness is sufficient for a good user experience: Solution 1 is fully correct and still produces socially awkward, arbitrary pairings; correctness and practicality are genuinely separate concerns, and both need to be evaluated independently.
Assuming the chain only creates transactions between adjacent sorted positions in a meaningful, relationship-based sense: adjacency here is purely a sorting artifact; a person's transaction partner can be someone they've never interacted with at all.
Section 8: Solution 2, The Practical Greedy Fix
What It Means

Fixing Solution 1's real weakness, not the math, the awkward pairing, using a smarter, still-fast approach. Splitting everyone into two groups first:

GET  (positive balance) — people who should RECEIVE money
GIVE (negative balance) — people who should PAY money

Repeating this loop until either side is empty:

1. Pick the person who has to GET the most.
2. Pick the person who has to GIVE the most.
3. That "giver" pays the "getter" min(get_amount, give_amount) —
   this guarantees AT LEAST ONE of them is fully settled after
   this single transaction.
4. Whoever ISN'T fully settled yet goes back into their pool with
   their updated (smaller) remaining balance.

A question worth working through directly: step 3 says "at least one is fully settled." There are three possible relationships between the getter's amount and the giver's amount. What are they, and what happens in each case?

Getter needs less than giver owes → getter is fully settled, giver has leftover debt.
Getter needs more than giver owes → giver is fully settled, getter still needs more.
They're exactly equal → both are fully settled in one shot.
X (get): 500,  Y (give): -600  → Y pays X 500. X done. Y still owes 100.
X (get): 600,  Y (give): -500  → Y pays X 500. Y done. X still needs 100.
X (get): 500,  Y (give): -500  → Y pays X 500. BOTH done.

Dry-running this on the real four-person example from Section 6: A: 
+
1750
, B: 
−
50
, C: 
−
1250
, D: 
−
450
.

A question worth checking directly: both solutions have been described using "
𝑛
−
1
 transactions, at most." Is 3 transactions here always the exact number for 4 people, every single time, or is it possible to need fewer? It's a maximum, not a guarantee. If balances happen to divide up more neatly (for example, two people exactly cancel each other out), settling could happen in fewer than 
𝑛
−
1
 transactions. 
𝑛
−
1
 is the ceiling; this greedy approach often does better than that, but it still isn't guaranteeing the true mathematical minimum, that remains NP-hard, per the deep-dive above.

Practical Mechanics: Two Heaps
GET pool  → max-heap  (always pop the biggest receiver, O(log n))
GIVE pool → min-heap  (always pop the biggest payer, O(log n))

Each round: pop from both heaps, settle min(get, give),
push back whichever side has leftover balance.

Total rounds: at most (n - 1)
Each round does ~3 heap operations (pop, pop, maybe one push back)

Time complexity: (n - 1) * (log n + log n + log n)  ~  O(n log n)

In LaTeX form, the total time complexity of this greedy approach is:

𝑂
(
(
𝑛
−
1
)
⋅
3
log
⁡
𝑛
)
=
𝑂
(
𝑛
log
⁡
𝑛
)

Worth being honest about scope: this greedy approach is not the actual algorithm real Splitwise uses internally, it's a genuinely good, practical approximation, and it's exactly what gets built in this course. A more sophisticated real-world approach is left as further reading for anyone curious.

Quiz Recap

A group of 3 has final balances: X: +900, Y: +300, Z: -1200. Using the greedy two-heap approach, what does Round 1 do?

A) X and Y split the ₹1200 debt from Z equally, ₹600 each
B) Z (biggest giver, -1200) pays X (biggest getter, +900) exactly ₹900, X is fully settled, Z still owes ₹300
C) Z pays both X and Y in the same round, since Z owes both of them
D) Y is skipped this round since X has a bigger balance, so Y is never actually settled
Correct answer: B. The rule is always "biggest getter, biggest giver, settle 
min
 of the two, at least one side fully clears." Here 
min
(
900
,
1200
)
=
900
, so X clears and Z carries forward 
−
300
 into the next round, where Z will then settle with Y.
Why A is wrong: it invents an equal-split rule that isn't part of this algorithm; that's a different, and NP-hard-to-optimize, idea entirely.
Why C is wrong: each round only ever produces one transaction, between the current biggest getter and biggest giver.
Why D is wrong: this is simply false, Y stays in the pool and gets settled in a later round; it is never dropped, only deferred.
Hidden Pitfalls
Assuming the greedy approach's 
𝑛
−
1
 upper bound is always exactly achieved: it is a ceiling, not a target; balances that happen to align neatly can settle in fewer transactions, as noted directly above.
Forgetting to re-check which side has leftover balance after each round: the algorithm's correctness depends on pushing the unsettled side back into its pool with its updated, smaller balance; skipping this step breaks the invariant that every round fully clears at least one person.
Treating this greedy approach as the actual algorithm real Splitwise uses: it is explicitly named as a good, practical approximation built for this course, not a claim about the real production system's internals.
Section 9: AI Corner, Algorithm Sanity-Check and Diagnosing a Flawed Approach
Touchpoint 1: Refine and Visualize

The greedy settle-up algorithm was just finished by hand. Running it past AI once, the same spirit as checking a class diagram in past lectures, except this time, everyone runs it themselves and compares real results in chat, rather than reacting to one instructor-shown response.

Prompt used:

"Here's a greedy debt-settlement algorithm I designed by hand:
repeatedly match the person who needs to receive the most money
with the person who needs to pay the most money, settle the
smaller of the two amounts, and repeat until everyone nets to
zero. Only point out something genuinely missing — don't
restructure what's already there. Also, draw this as a simple
flowchart."

Since different people running the exact same prompt genuinely get different responses, no single "correct" AI output exists to memorize here. What matters is recognizing which kinds of gaps are genuinely worth taking seriously versus which are minor implementation details. Several possibilities commonly surface, and each is worth understanding fully regardless of whether a particular run happened to raise it:

Tie-breaking: what happens when two people have exactly equal "get" amounts, or exactly equal "give" amounts? This does not actually affect correctness, any consistent choice among ties still produces a valid settlement in at most 
𝑛
−
1
 transactions. It only matters if deterministic, reproducible output is desired (the same input always producing the exact same transaction list), which is a reasonable but secondary concern.
Floating-point rounding: money is often modeled with fractional units (cents or paise). Splitting an amount among an odd number of people can produce fractional paise that don't divide evenly. A real implementation needs an explicit rounding rule, for example, rounding to the nearest paisa and having one designated person's share absorb the rounding residue, to preserve the 
∑
paid
=
∑
owed
 invariant exactly.
The zero-balance edge case: a person whose extra_amount is exactly zero should be excluded from both the GET and GIVE pools entirely; they are already settled, and including them serves no purpose.
Flowchart loop termination: whether a generated flowchart clearly shows the loop actually stopping once both heaps are empty is a legitimate thing to check on any AI-generated diagram; a diagram missing an explicit termination condition is genuinely incomplete, regardless of whether the underlying algorithm description was correct.

Whatever a specific run actually surfaces, the same question applies every time: does the gap raised actually matter for correctness, or is it a nice-to-have implementation detail? Either way, that judgment call belongs to the engineer, not the AI tool.

Same rule as every AI Corner: AI can react fast to something
already built, but the decision of whether a raised point is a
real gap or a non-issue stays with the engineer. Different runs,
different people, can surface completely different observations
— that's expected, not a flaw in the exercise.

Touchpoint 2: Diagnose, Don't Generate

This time, a flawed settle-up approach gets diagnosed, one written out by hand, not AI-generated, a deliberately broken idea.

Proposed approach:
"Every time a new expense is added, immediately generate a
transaction to settle it: the person who's owed money for THIS
expense gets paid right away by whoever owes it, for THIS expense
only. Repeat for every new expense as it comes in."

Prompt used:

"Diagnose only — don't rewrite yet. What's wrong with settling
each expense individually like this, the moment it's created?"

Whatever a specific AI tool says here, the useful question is: does it connect back to something already established earlier in this document? It should connect directly back to Section 6, "the whole group of transactions has to be settled up at once, never just one in isolation." Settling per-expense is precisely the mistake that idea was warning against.

There's a second angle worth naming explicitly, which not every AI response will necessarily surface on its own: this approach also misses cancellation. If A owes B money from one expense, and B owes A money from a separate expense, settling each expense individually loses the opportunity to simply net the two out and have only the smaller side pay the difference once. Settling expense-by-expense treats every expense as if it exists in total isolation from every other expense involving the same two people, which is exactly the opposite of the group-wide view Section 6 established as necessary.

The fix is everything already built: compute each person's extra_amount across all expenses first (Section 6), then run the greedy get/give matching (Section 8). Never settle a single expense in isolation.

Same rule as every AI Corner: AI is fast at spotting an issue, but
the judgment call — connecting it back to the system's actual
design decision — belongs to the engineer. Whatever a specific
AI tool said here, the real lesson underneath it is one already
named directly in Section 6.

Hidden Pitfalls
Treating any single AI response as the definitive "correct" gap to have found: this touchpoint is deliberately open-ended; different runs surfacing different valid observations is expected behavior, not something to force into a single scripted answer.
Settling an expense immediately upon creation instead of waiting for a group-wide settle-up request: this repeats the exact mistake Section 6 was built specifically to prevent, and additionally forfeits the cancellation opportunities that only become visible once every expense between two people is considered together.
Wrap-Up

Today's real lesson wasn't a new design pattern, it was requirements discipline (asking the right clarifying question at the right moment) plus a genuine algorithm: compute net balances first, then greedily match the biggest getter with the biggest giver.

The class diagram was deliberately not built live today, different from every other Design lecture in this course so far, and that was on purpose, because the algorithm needed the room. Minimizing transactions perfectly is NP-hard, per the deep-dive above; the greedy fix is fast, practical, and gives an upper bound of 
𝑛
−
1
 transactions, but it doesn't promise the true mathematical minimum. That is an honest, named simplification, not a bug.

DESIGN SPLITWISE — covered today:
- Requirements R1-R12, in strict order, with real clarifying
  questions modeled throughout
- Paid vs. owed, and the "sums must match" invariant
- extra_amount formula: computing each person's true net balance
  across every expense
- Solution 1: sorted chain, n-1 transactions, correct but
  practically awkward
- Solution 2: greedy get/give matching using two heaps,
  O(n log n), same n-1 upper bound but much more sensible pairing
- A deep-dive into why minimizing transactions is genuinely
  NP-hard, connecting it to the Subset Sum problem
- AI Corner: sanity-checked the greedy algorithm (tie-breaking,
  rounding, edge cases), then diagnosed why per-expense settling
  repeats a mistake already named earlier in the session

Left for next class, not built together today:
- The actual class diagram (built live, via noun-spotting)
- The actual schema design (built live)
- Taking real input from the command line

Common Pitfalls Summary
1. Assuming "non-negative owed amounts" is sufficient for a valid
   expense entry.
   -> The real rule is sum(owed) = sum(paid) = total; individual
      non-negativity says nothing about whether the split is
      internally consistent.

2. Assuming a group member automatically shares in every expense
   logged in that group.
   -> Group visibility (R3) and expense participation (R4) are
      separate; only the specific participants of an expense owe
      for it, though other members may still see it happened.

3. Confusing R10's scope (settle one person, everywhere) with
   R11's scope (settle a whole group, using only that group's
   expenses).
   -> Applying the wrong scope produces an incorrect settlement
      list for the actual request being made.

4. Settling expenses one at a time, as they're created, instead
   of waiting for a group-wide settle-up request.
   -> Generates far more transactions than necessary and loses
      cancellation opportunities between the same two people
      across different expenses.

5. Forgetting that every person's final extra_amount must sum to
   exactly zero across the whole group.
   -> A nonzero sum indicates a real bug in the input or the
      calculation itself — a genuine sanity check, not a
      coincidence of the worked examples.

6. Assuming the greedy two-heap approach guarantees the true
   mathematical minimum number of transactions.
   -> It guarantees an upper bound of n-1 and is often better in
      practice, but minimizing transactions perfectly is NP-hard;
      no algorithm here claims to find the provable optimum.

7. Assuming mathematical correctness (Solution 1) implies a good
   user experience.
   -> The sorted chain is fully correct and still produces
      arbitrary, socially awkward pairings between people who
      never actually transacted with each other.

8. Forgetting to push the unsettled side's updated balance back
   into its pool during the greedy algorithm.
   -> Breaks the invariant that every round fully clears at least
      one person, corrupting the remaining rounds.

9. Treating any single AI response in an open-ended exercise as
   "the" correct finding to memorize.
   -> Different runs surface genuinely different valid
      observations; the judgment of whether a finding matters
      belongs to the engineer, not to matching one scripted answer.

Higher-Level Hidden Pitfalls (cross-cutting, not listed above):

Assuming every requirement in a real interview needs a new class or field: several requirements in this session (R5, R6, R7) describe queries or views over data that already exists rather than new structural elements, a distinction worth carrying directly into next session's noun-spotting exercise.
Treating "good to have" requirements (R12) with the same rigidity as hard requirements: explicitly naming which requirements are aspirational versus mandatory, out loud, to an interviewer, is itself a demonstrated skill, not just a technical footnote.
Key Terminology
Term	Meaning in Simple Words
extra_amount (net balance)	A single number computed per person, summing (amount they paid minus amount they owed) across every expense they're part of; positive means they should receive money overall, negative means they should pay.
GET pool / GIVE pool	The two groups people are split into for the greedy settlement algorithm: GET holds everyone with a positive net balance (owed money), GIVE holds everyone with a negative net balance (owes money).
Sorted Chain Settlement	A brute-force settlement approach that sorts everyone by net balance and has each adjacent pair settle fully with each other in sequence, always producing exactly 
𝑛
−
1
 transactions for 
𝑛
 people.
Greedy Get/Give Matching	A practical settlement approach that repeatedly matches the person owed the most money with the person who owes the most money, settling the smaller of the two amounts each round, bounded by 
𝑛
−
1
 transactions but often needing fewer.
NP-Hard	A classification for problems where no algorithm is known that finds the provably optimal answer quickly (in polynomial time) for every possible input as the input size grows; it does not mean no fast, good-enough approximate solution exists.
Subset Sum Problem	A classic computationally hard problem asking whether some subset of a given set of numbers adds up to a specific target value; used here to explain why finding the truly minimal transaction count is NP-hard.
Follow-up (interview step)	The stage of a machine coding interview, after a working solution already exists, where the interviewer probes edge cases and scale to assess how deep the candidate's understanding actually goes.
Noun-Spotting	A method (introduced here by name, used starting next session) of deriving class-diagram candidates directly by identifying the nouns present in a written requirements document.

The six-step design framework, DTOs, Repository/Service/Controller layering, JPA, and Spring Boot were already defined in Post-Read 8 through Post-Read 11 and are not redefined here.

Frequently Asked Interview Questions

1. Explain the distinction between "who paid" and "who owes" for a single expense, and state the invariant that must always hold between them.
"Who paid" records the actual money physically handed over by each participant, for example, one person covering the entire bill on their card. "Who owes" records each participant's fair share of the total cost, which may be split unequally based on factors like who ordered more. The invariant that must always hold is that the sum of amounts paid equals the sum of amounts owed, and both equal the total expense amount; any expense entry where these sums disagree indicates a data-integrity bug that the system should reject.

2. Why does group membership (R3) not automatically imply participation in every expense logged within that group (R4)?
R3 establishes that groups exist purely to simplify adding participants to expenses, and that any group member can see expenses logged in the group. R4, however, requires an expense to explicitly specify which users are actually involved in it, meaning a group can have members who are visible observers of an expense without being financially responsible for any part of it. Visibility and financial participation are deliberately kept as two separate concerns.

3. Precisely distinguish the scope of an individual settle-up (R10) from a group settle-up (R11).
An individual settle-up (R10) computes and displays a list of transactions that, once all executed, bring exactly one requesting user's overall net balance to zero, considering every expense that user is part of across the entire system, regardless of which group it belongs to. A group settle-up (R11) computes a list of transactions that bring every member of one specific group to zero, but considers only expenses belonging to that particular group; a member's balance from an entirely separate group or one-off expense is left untouched by a group settle-up.

4. Derive the extra_amount formula, and explain precisely why summing it across every person in a group must always equal zero.
For a person 
𝑝
, extra_amount is computed as 
∑
𝑒
(
paid
𝑒
(
𝑝
)
−
owed
𝑒
(
𝑝
)
)
, summed across every expense 
𝑒
 that person appears in. Because every individual expense satisfies 
∑
paid
=
∑
owed
 across all its participants (the core R4 invariant), summing 
(
paid
−
owed
)
 across all participants of any single expense always yields zero for that expense. Since every expense independently contributes a net zero across its own participants, summing every person's total extra_amount across every expense in the group must also net to exactly zero overall.

5. Why is settling every expense individually, the moment it's created, a genuinely worse approach than waiting to settle the whole group at once?
Settling an expense in isolation ignores every other expense involving the same participants. If person A owes person B money from one expense, and person B separately owes person A money from a completely different expense, settling each expense individually forces two separate transactions where only one, netting the difference, would actually be necessary. Waiting to compute each person's overall net balance across every expense before settling captures these cancellation opportunities, directly reducing the total number of transactions needed.

6. Explain why the sorted-chain approach (Solution 1) is mathematically correct yet still considered practically inadequate.
The sorted-chain approach correctly brings every person's balance to exactly zero, using exactly 
𝑛
−
1
 transactions for 
𝑛
 people, satisfying every requirement about correctness. Its weakness is entirely about user experience: the pairing between who pays whom is determined purely by sorted numerical position, with zero awareness of whether those two people ever actually shared a real expense together. This can force someone to make a payment directly to a person they've never interacted with, which is technically valid but socially and practically awkward for real users.

7. Walk through exactly how the greedy get/give matching algorithm decides who pays whom in each round, and explain why at least one person is always fully settled after each round.
Each round identifies the person with the largest positive balance in the GET pool and the person with the largest negative balance (in absolute value) in the GIVE pool. The giver pays the getter an amount equal to the smaller of the two magnitudes involved. Since one of the two amounts is necessarily less than or equal to the other, the smaller one is fully covered by this single transaction, meaning whichever side had the smaller magnitude reaches exactly zero and exits the process; the other side, if any balance remains, returns to its pool with its updated, smaller remaining balance for a future round.

8. What is the time complexity of the greedy two-heap settlement approach, and why do heaps specifically fit this problem well?
The time complexity is 
𝑂
(
𝑛
log
⁡
𝑛
)
: at most 
𝑛
−
1
 rounds occur, and each round performs a constant number of heap operations (popping the maximum from each of two heaps, and potentially pushing one value back), each costing 
𝑂
(
log
⁡
𝑛
)
. A max-heap naturally supports always retrieving the current largest "get" balance efficiently, and a min-heap (or a max-heap over negated values) naturally supports always retrieving the current largest "give" balance efficiently, exactly the two repeated operations this algorithm needs every single round.

9. Explain, at a conceptual level, why finding the truly minimal number of settlement transactions is NP-hard.
Minimizing total transactions is equivalent to finding the maximum number of independent sub-groups of people whose balances each sum to zero on their own, since each such independent sub-group can be settled entirely separately using fewer total transactions than treating the whole group as one connected block. Determining whether any given subset of balances sums to zero is itself a version of the classic Subset Sum problem, known to be computationally hard; finding the single best way to partition an entire group into the maximum number of such zero-sum subsets is at least as hard, since it implicitly requires checking combinatorially many possible subsets as the group size grows.

10. Why does the greedy approach's 
𝑛
−
1
 transaction bound not represent a guaranteed exact count, and under what condition might fewer transactions actually be needed?
The 
𝑛
−
1
 bound represents a worst-case ceiling, not a fixed target; it holds because, in the worst case, each round settles at least one person completely, so at most 
𝑛
−
1
 rounds are needed to settle all 
𝑛
 people. If the specific set of balances happens to divide more neatly, for example, if two people's balances exactly cancel each other out in a single transaction, or if the group's balances naturally split into independent zero-sum sub-groups (as discussed in the NP-hardness deep-dive), fewer than 
𝑛
−
1
 total transactions may be needed to fully settle everyone.

11. Why is R9's "leave group" rule (a person cannot leave a group while part of any expense in it) directly connected to the existence of group settle-up (R11)?
The leave-group rule requires that a departing member first have zero outstanding balance within that specific group's expenses before they can leave. Group settle-up (R11) is precisely the mechanism that computes and resolves exactly this kind of within-group balance, generating the transactions needed to bring every group member, including someone wanting to leave, to zero using only that group's own expenses. Without group settle-up existing as a feature, there would be no defined path for a member to ever reach the zero-balance state the leave-group rule requires.

12. In this session's roleplayed interview structure, what distinguishes the "Follow-up" step from the "Clarify Requirements" step, and why does it matter that both exist separately?
"Clarify Requirements" happens before any design or code exists, and is about resolving ambiguity in the stated problem itself, such as asking how groups actually work or what happens when someone leaves one. "Follow-up" happens after a working solution already exists, and is about the interviewer probing the depth of the candidate's understanding under new, harder conditions, such as asking what changes if a group has 500 members. Distinguishing these matters because they test different skills: the first tests whether a candidate can identify what's unclear before committing to a design, while the second tests whether a candidate's solution and reasoning actually hold up under scrutiny once it exists.

Self-Check Questions
In your own words, explain why "who paid" and "who owes" must be tracked as two separate lists per expense, rather than as a single combined value per person.
Trace through: compute the extra_amount for a person Q who appears in 4 expenses: (paid ₹0, owed ₹200), (paid ₹500, owed ₹0), (paid ₹0, owed ₹150), (paid ₹800, owed ₹450). State whether Q pays or receives overall, and how much.
Write a snippet: sketch pseudocode (not full Java) for computing every person's extra_amount given a list of expenses, each expense holding a paid-map and an owed-map.
Compare the sorted-chain approach (Solution 1) and the greedy get/give approach (Solution 2). Identify one concrete scenario where both produce the exact same number of transactions, and one where the greedy approach produces fewer.
Explain, in your own words, why settling a group's expenses one at a time as they occur can produce more transactions than waiting and settling the whole group at "settle up" time.
Trace through: for the 3-person example in Section 8's quiz (X: +900, Y: +300, Z: -1200), work out Round 2 by hand after Round 1 has completed, and state the final transaction list in full.
Write a short paragraph explaining, in your own words, why the maximum-zero-sum-subgroup framing connects transaction minimization to the Subset Sum problem.
Compare R10 and R11 directly: describe a specific scenario involving one user in two different groups where the two settle-up scopes would produce genuinely different transaction lists.
Explain, in your own words, why a person whose extra_amount is exactly zero should be excluded entirely from both the GET and GIVE pools in the greedy algorithm.
Trace through: if a group's balances were 
+
1000
,
−
400
,
−
300
,
−
300
, walk through the greedy algorithm round by round and state the final number of transactions used.
In your own words, explain why "good to have" (R12) is a meaningfully different commitment than a hard requirement, and describe how you would phrase that distinction out loud to an interviewer.
Write a short paragraph describing, using your own words, why an AI Corner exercise with no single scripted correct answer can still be a valuable learning exercise, using this session's Touchpoint 1 as your example.
Further Reading
Post-Read 8, Machine Coding 8: Design BookMyShow - the original source of the six-step design framework and the three standard clarifying questions (full system vs. entities, persistence, interaction mode) reused directly in this session.
Post-Read 9 through Post-Read 11, Code BookMyShow 1-3 - the full JPA, Hibernate, and Spring Boot foundation this project's code (starting in Code Splitwise 1) reuses without re-deriving.
Introduction to the Theory of Computation (Michael Sipser) - a canonical reference for NP-hardness, NP-completeness, and the Subset Sum problem, directly relevant to this document's supplementary deep-dive.
Splitwise's own public writing on its real debt-simplification algorithm (referenced in this session's homework as a linked resource to review independently) - useful for comparing this course's greedy two-heap approximation against a real production system's actual approach.
Introduction to Algorithms (Cormen, Leiserson, Rivest, Stein), chapters on greedy algorithms and heaps - relevant background for understanding why greedy approaches provide good, fast, practical solutions even without provable optimality, and for the heap-based implementation of Section 8's algorithm.
Java's PriorityQueue documentation - the standard Java implementation of a heap, directly relevant to actually implementing the max-heap/min-heap greedy approach described in Section 8 in real code next session.
Homework
1. Re-read R1-R12 on your own and, for each one, ask yourself:
   "does this require a NEW class, or is it just an attribute or
   behavior on something that already exists?" Bring your own
   guesses to compare against next class's method.

2. By hand, on paper, compute the final extra_amount for a group
   of 5 people, across at least 4 made-up expenses. Confirm your
   final numbers sum to exactly zero before moving on.

3. Dry-run the greedy two-heap approach on your own 5-person
   example from #2. Count how many transactions it actually takes,
   and compare that to the n-1 upper bound.

4. Read the linked answer on Splitwise's real debt-simplification
   algorithm (mentioned in class) and write 3 bullet points on how
   it differs from our greedy two-heap approach.

5. Push your notes to GitHub — branch name:
   splitwise-design-complete

Last changed by 
 
Tushar Harsan·Follow
0
31
Add a comment
Published on  HackMD
