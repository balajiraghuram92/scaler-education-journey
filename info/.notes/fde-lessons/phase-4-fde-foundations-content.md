# FDE Phase 4 — Module 1: FDE Foundations, Python, Workflow & Delivery (Lessons 7-12 of 12, module complete)

Six lessons, authored content + MCQs, ready for local-LLM ingestion via
`phase-4-fde-foundations-prompt.md` in this same directory.

Course: `fde-curriculum` · Module: `fde-foundations` ("1. FDE Foundations: Python, Workflow & Delivery")

---

# LESSON 7

```yaml
lesson_id: fde-foundations-07-pydantic-v2-structured-logging-and-profiling
lesson_title: "Pydantic v2, Structured Logging & Profiling"
lesson_order: 7

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: fde-foundations
module_name: "FDE Foundations: Python, Workflow & Delivery"
module_order: 1

difficulty: Medium-Hard
estimated_minutes: 75
content_status: Draft

learning_outcomes:
  - "Use Pydantic v2 models as a validation boundary so downstream code can trust data shape instead of re-checking it."
  - "Emit structured (key-value/JSON) logs instead of free-text strings, and explain why this matters when someone other than the FDE reads the logs."
  - "Profile code under realistic data volume before optimizing, using cProfile, rather than guessing at the bottleneck."

created_date: "2026-08-31"
last_updated: "2026-08-31"
author: "Raghuram Balaji"

supplementary_content:
  has_mcq_section: true
  mcq_count: 8
  has_coding_exercises: false
  exercise_count: 0
  has_further_reading: false
  resource_count: 0
```

<!-- CHAPTER_BODY_START -->
# Pydantic v2, Structured Logging & Profiling

## Concepts Covered

Pydantic v2's `BaseModel` turns untrusted external data — a customer API response, a config file, a CSV row — into a validated, typed object at the exact boundary where that data enters your code, backed by `pydantic-core`, a Rust implementation that makes this validation fast enough to use pervasively rather than sparingly. The value isn't just catching bad data; it's a "parse, don't validate" discipline: once a `CustomerRecord` has successfully been constructed from raw input, every function downstream can trust its field types and constraints without re-checking them, because construction itself was the check — a validation error surfaces once, at the boundary, with a clear message about exactly which field failed and why, instead of a confusing type error three function calls deep in unrelated code. `pydantic-settings` extends the same model to configuration, reading typed settings from environment variables with validation — directly useful for an FDE whose code needs different configuration on every customer's infrastructure, since a missing or malformed environment variable fails loudly at startup instead of producing a mysterious runtime error hours into a demo.

Structured logging replaces free-text log lines ("processing record 4521, took a while") with log records as key-value or JSON data (`logger.info("record_processed", record_id=4521, duration_ms=340)`), which sounds like a small change but has a real consequence: a structured log can be filtered, aggregated, and queried ("show me every record where `duration_ms > 1000`") the way free text cannot, without anyone writing a fragile regex against a message string that might change wording later. This matters more for an FDE than for an engineer on a long-lived internal team, specifically because an FDE's logs are frequently read by someone else — a customer's on-call engineer at 2am, an observability tool with no context on the FDE's personal debugging habits — and a log line only useful to the person who wrote it defeats the point of logging at all.

Profiling is the discipline of measuring where time actually goes before changing code to make it faster, and the specific failure this guards against is optimizing the wrong thing based on intuition — a function that "feels" slow because it's visually complex is often not where the actual time is spent; `cProfile` reports both cumulative time (a function plus everything it calls) and total/own time (just that function's own execution, excluding calls it makes), and the distinction matters because a function with high cumulative but low own time isn't the bottleneck itself, something it calls is. Profiling under realistic data volume, not a small hand-picked test input, is equally important: a function's relative cost can invert entirely between 100 rows and 100,000 rows, so a profile run against toy data can point optimization effort at exactly the wrong function.

## Practical Backend Scenario

A customer reports "the nightly sync job is slow" with no further detail, and the FDE has no debugger access to the customer's production environment — only log output the customer is willing to share after the fact. Because the sync job's records were validated into Pydantic models at ingestion and every stage logged structured events (`logger.info("stage_started", stage="fetch", batch_id=...)`, `logger.info("stage_completed", stage="fetch", batch_id=..., duration_ms=...)`), the FDE reconstructs exactly which stage is slow purely by filtering the shared logs for `duration_ms` outliers across stages, without needing a second round-trip to production access — the fetch stage, not the widely-suspected transform stage, turns out to be the actual bottleneck. Only then does the FDE request a one-time profiling run scoped specifically to the fetch stage under the customer's real batch size, confirming the exact function responsible rather than guessing and optimizing the transform code that was never the problem.

## Practice Loop

1. Define a Pydantic v2 model for a customer record with at least one required field, one optional field with a default, and one field with a validation constraint (e.g. a value that must be positive), and confirm both a valid and an invalid input produce the behavior you expect.
2. Use `pydantic-settings` to read at least two configuration values from environment variables into a typed settings object, and confirm a missing required setting fails loudly at startup rather than silently.
3. Replace a free-text log statement with a structured log call (key-value or JSON), and write a short script that filters a batch of your own structured log output for entries matching a specific condition (e.g. duration above a threshold) — the exact query a real diagnostic would need.
4. Profile a small function with `cProfile` against a small input (10 items) and a larger input (10,000 items), and identify whether the same function remains the bottleneck at both scales or whether the profile results change.
5. Write a one-paragraph explanation of why the FDE in the scenario was able to diagnose the slow stage without a second round of production access, tying it directly back to the structured logging decision made earlier in the job's development.

## Evidence of Understanding

You can explain the "parse, don't validate" boundary Pydantic models create and why it lets downstream code skip re-validation. You can write structured log statements and explain concretely why they're more useful than free text to someone who isn't the FDE who wrote them. You can distinguish cumulative from total/own time in a profiler's output, and you can explain why profiling under realistic data volume, not toy input, is necessary before trusting a profiling result.

## Suggested Extension

Add a Pydantic validator that rejects a record if a business rule is violated (not just a type mismatch — e.g. a `delivery_date` that's in the past), and write a structured log event specifically for validation failures that captures which rule failed and what the offending value was, so a customer's team could query "how many records failed validation last night, and why" directly from logs without any code changes.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** "Parse, don't validate" boundary
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Once a Pydantic model has successfully validated a piece of external data into an object, why can downstream code trust its shape without re-checking?

**OPTIONS:**
- [x] B: Construction itself was the check — if the object exists, it already satisfied the model's type and constraint rules, so re-validating downstream would be redundant
- [ ] A: Pydantic models cannot be constructed with invalid data under any circumstances, even before validation runs
- [ ] C: Downstream code should always re-validate regardless, Pydantic provides no real guarantee
- [ ] D: This is only true for models with no optional fields

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The entire value of the "parse, don't validate" pattern is that a successfully constructed model instance is proof the data already passed validation — checking again downstream would just repeat work the constructor already did.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [pydantic, parse-dont-validate]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Why pydantic-settings matters for FDE work
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why is a typed settings object that fails loudly at startup on a missing environment variable specifically valuable for an FDE, compared to code that reads `os.environ.get()` with silent defaults?

**OPTIONS:**
- [x] B: An FDE's code runs against different, unfamiliar configuration on every customer's infrastructure, so a loud startup failure surfaces a misconfiguration immediately rather than as a mysterious runtime error hours into a demo
- [ ] A: `pydantic-settings` is required by law for handling environment variables
- [ ] C: Silent defaults are always safer than loud failures in any context
- [ ] D: This has no particular relevance to FDE work specifically

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The recurring FDE context — new, unfamiliar customer infrastructure every engagement — is exactly where a loud, immediate startup failure on bad configuration is more valuable than in a stable, long-lived internal environment where configuration rarely changes.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [pydantic-settings, fail-loud]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Structured vs. free-text logging
**DIFFICULTY:** Easy
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What can a structured log statement support that a free-text log line cannot, without a fragile regex against message wording?

**OPTIONS:**
- [x] B: Filtering, aggregating, and querying by specific field values (e.g. "show every record where duration_ms > 1000")
- [ ] A: Structured logs execute faster than free-text logs at runtime
- [ ] C: Free-text logs cannot be written to a file, only structured logs can
- [ ] D: There is no practical difference between the two formats

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
Structured logs carry queryable fields directly, so filtering by a specific value is a direct query rather than requiring a regex against a message string whose wording might change and silently break the query.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [structured-logging, queryability]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why logging audience matters more for FDEs
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson argue structured logging matters more for an FDE than for an engineer on a long-lived internal team?

**OPTIONS:**
- [x] B: An FDE's logs are frequently read by someone else entirely — a customer's on-call engineer, an observability tool with no context on the FDE's personal habits — so a log only useful to the person who wrote it defeats the point
- [ ] A: Internal teams never read logs at all
- [ ] C: FDE code produces more log volume than internal team code by default
- [ ] D: This distinction doesn't actually matter; the lesson treats the two cases identically

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The recurring theme of an FDE handing off work to people who didn't write it (echoing the "enable" step from the FDE-role lesson) applies directly to logs — they need to be legible to someone without the FDE's personal context.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [logging-audience, FDE-specific]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Cumulative vs. total time
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
A profiler reports function `process_batch` with high cumulative time but low total/own time. What does this indicate?

**OPTIONS:**
- [x] B: `process_batch` itself isn't the bottleneck — most of its cumulative time comes from functions it calls, so the actual slow code lives in one of those called functions, not in `process_batch`'s own logic
- [ ] A: `process_batch` is definitely the function that needs to be optimized
- [ ] C: High cumulative time with low own time is a measurement error and should be ignored
- [ ] D: `process_batch` is called far more often than any other function in the program

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
Cumulative time includes everything a function calls; own/total time is just its own execution. A high cumulative but low own time means the real cost is downstream in a called function, not in this function's own code.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [cprofile, cumulative-vs-own-time]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Why profile at realistic scale
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson insist on profiling under realistic data volume rather than a small hand-picked test input?

**OPTIONS:**
- [x] B: A function's relative cost can invert entirely between small and large input sizes, so a profile against toy data can point optimization effort at exactly the wrong function
- [ ] A: Profilers technically cannot run against small inputs
- [ ] C: Small test inputs always produce identical relative costs to large inputs, so this is only a minor concern
- [ ] D: Realistic-scale profiling is only needed for functions that use loops

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
Algorithmic behavior that's invisible at small scale (like quadratic growth) can dominate at real scale, so a profile at the wrong scale risks misidentifying the actual bottleneck.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [profiling-scale, realistic-input]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Diagnosing the slow sync job without a debugger
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why was the FDE able to identify the actual slow stage of the sync job from shared logs alone, without a second round of production access?

**OPTIONS:**
- [x] B: Because every stage's Pydantic-validated events were logged with structured, queryable fields including per-stage duration, filtering the shared logs for duration outliers directly revealed which stage was slow, without needing live debugging access
- [ ] A: Because the customer happened to already know which stage was slow
- [ ] C: Because Pydantic models automatically profile themselves
- [ ] D: This was luck and would not generally be possible from logs alone

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the direct payoff of the earlier structured-logging investment — a diagnostic question answerable purely by filtering existing structured log data, without needing new production access at all.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [diagnosis-from-logs, structured-logging-payoff]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Why request profiling only after log-based diagnosis
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why did the FDE only request a scoped profiling run after narrowing the problem to the fetch stage via logs, rather than requesting a full profiling run of the entire job upfront?

**OPTIONS:**
- [x] B: A scoped, targeted profiling request (specifically the fetch stage) is more likely to be granted quickly by the customer and produces a more directly useful result than an unscoped, broad request made before the actual bottleneck was known
- [ ] A: Profiling an entire job is technically impossible
- [ ] C: Logs and profiling data are mutually exclusive and cannot be used together
- [ ] D: There was no particular reason; either order would have worked identically

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
Narrowing scope first via cheap, already-available log data before requesting a more invasive or costly diagnostic (production profiling access) is a practical sequencing decision that respects both the customer's constraints and gets to the answer faster.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [scoped-diagnosis, diagnostic-sequencing]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->

---

# LESSON 8

```yaml
lesson_id: fde-foundations-08-git-internals-github-workflows-and-ai-dev-tools-cursor-claude-code-mcp
lesson_title: "Git Internals, GitHub Workflows & AI Dev Tools (Cursor, Claude Code, MCP)"
lesson_order: 8

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: fde-foundations
module_name: "FDE Foundations: Python, Workflow & Delivery"
module_order: 1

difficulty: Medium-Hard
estimated_minutes: 75
content_status: Draft

learning_outcomes:
  - "Explain Git's object model well enough to reason confidently about what rebase and merge actually do to history."
  - "Use a PR-based GitHub workflow with CI gating merge, and explain why this matters more when an FDE often works with less peer oversight."
  - "Review AI-generated diffs from tools like Cursor/Claude Code critically before committing to a customer's repository, including via MCP-connected external context."

created_date: "2026-08-31"
last_updated: "2026-08-31"
author: "Raghuram Balaji"

supplementary_content:
  has_mcq_section: true
  mcq_count: 8
  has_coding_exercises: false
  exercise_count: 0
  has_further_reading: false
  resource_count: 0
```

<!-- CHAPTER_BODY_START -->
# Git Internals, GitHub Workflows & AI Dev Tools (Cursor, Claude Code, MCP)

## Concepts Covered

Git's object model is simpler than the command surface suggests: a commit is a snapshot pointer containing a reference to a tree (the state of the whole file hierarchy at that point) and a pointer to its parent commit(s), a tree contains blobs (file contents, addressed by the SHA hash of their content) and further trees for subdirectories, and everything is content-addressed — identical content always hashes to the same object, which is why Git deduplicates storage automatically. A branch is not a container holding commits; it is a movable pointer to a single commit, updated to point at a new commit each time you commit while that branch is checked out — understanding this is what makes `rebase` versus `merge` a genuinely reasoned choice instead of memorized incantations: `merge` creates a new commit with two parents, preserving both branches' actual history exactly as it happened; `rebase` re-plays your branch's commits one at a time on top of a new base, creating entirely new commits with new hashes (the content may look identical, but the commit objects are different), which rewrites history rather than preserving it — safe on a branch only you're working on, dangerous on any branch someone else has already pulled, because their local history and the rewritten remote history will diverge.

GitHub's PR-based workflow — propose a change on a branch, open a pull request, require review and passing CI checks before merging into a protected `main` — exists to catch problems before they reach the branch everyone builds on top of. This matters more for an FDE than it might for an engineer embedded in a large team with routine code review: FDE work is often solo or in a very small on-site group, so the structural safety net a PR-plus-CI workflow provides (a required check that doesn't care whether a human reviewer happened to be available) substitutes for peer oversight the FDE may not otherwise have, and it protects the customer's repository from an unreviewed, direct push to `main` — a mistake with real consequences when that repository is the customer's actual production system, not a personal side project.

AI coding assistants (Cursor, Claude Code, and similar tools operating agentically inside the editor or terminal) can propose and apply real diffs directly to a working tree, and the Model Context Protocol from the agentic-systems module is the mechanism that lets these tools reach beyond the local codebase — connecting to a customer's internal documentation server, ticket tracker, or API reference as additional context the assistant can query while drafting a change, rather than working from local files alone. This capability raises the stakes on a discipline that mattered before AI tools existed but matters more now: reviewing a proposed diff critically before it's committed, especially in an unfamiliar customer repository where a plausible-looking but subtly wrong change (a rebase suggestion that would rewrite shared history, a "fix" that touches a file outside the actual bug's scope) is more costly than the same mistake in a personal sandbox — the tool proposing a change is functionally identical to the "model proposes, your code/you decide" pattern from the function-calling lesson, just applied to git operations instead of API calls.

## Practical Backend Scenario

An FDE uses Claude Code, connected via MCP to the customer's internal ticket tracker, to draft a fix for a specific reported bug — the assistant reads the actual ticket description directly through the MCP connection rather than the FDE having to paste it in manually, and proposes a diff. Reviewing the diff before accepting it, the FDE notices two things: the actual bug fix itself looks correct and scoped tightly to the reported issue, but the assistant also suggested rebasing the feature branch onto a squashed version of `main` to "clean up the history" — a branch two other contractors on the same customer engagement have already pulled and are actively working from. Accepting the fix itself is safe; accepting the rebase suggestion would rewrite commits those two contractors already have locally, creating a painful history-divergence problem for both of them the next time they pull. The FDE accepts the bug-fix diff, declines the rebase suggestion, and opens a PR through the normal protected-`main` workflow so CI runs before the fix merges.

## Practice Loop

1. Create a small local Git repository, make a few commits, and inspect the actual object types involved using Git's low-level commands (`git cat-file -t` and `git cat-file -p` on a commit, then the tree it points to, then a blob within that tree) to see the commit → tree → blob structure directly rather than through the porcelain commands.
2. Create two branches from the same commit, make a distinct commit on each, then merge one into the other and inspect the resulting merge commit's two parents.
3. Reset one of the branches back to its starting point, make the same distinct commit again, and this time rebase it onto the other branch instead of merging — compare the resulting commit hash to the original commit made in step 1, and confirm they differ even if the file content is identical.
4. Set up a GitHub repository with branch protection on `main` requiring a passing CI check (even a trivial one) before merge, and open a PR that intentionally fails the check first, then fix it and confirm the PR becomes mergeable only after the check passes.
5. Write a one-paragraph description of a specific AI-assistant-proposed change you would want to review very carefully before accepting in an unfamiliar customer repository, and explain what makes that particular kind of change higher-risk than others.

## Evidence of Understanding

You can explain Git's commit/tree/blob object model well enough to reason about what `rebase` and `merge` actually do differently to commit history, and you can state specifically why rebasing a shared branch is dangerous while rebasing your own private branch is safe. You can set up and justify a PR-plus-CI workflow with protected `main`, and explain why this substitutes for peer oversight an FDE may not otherwise have on a solo or small on-site engagement. You can describe how MCP extends an AI coding assistant's context beyond local files, and you can identify the specific category of AI-proposed change (history-rewriting operations, changes outside the stated scope) that warrants the most careful review before acceptance in a customer's repository.

## Suggested Extension

Write a short checklist (5-6 items) an FDE should run through before accepting any AI-assistant-proposed diff in a customer repository — informed by the scenario's rebase example — and identify which single item on your checklist would have caught that specific risk fastest.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** What a Git branch actually is
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What is a Git branch, at the object-model level?

**OPTIONS:**
- [x] B: A movable pointer to a single commit, updated to point at a new commit each time you commit while that branch is checked out
- [ ] A: A container that physically holds a copy of every commit made on it
- [ ] C: A separate, isolated copy of the entire repository's file contents
- [ ] D: A tag that permanently marks one specific commit and never moves

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Understanding a branch as a movable pointer, not a container, is what makes operations like rebase (which moves where commits sit relative to other branches) reasoned rather than memorized.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [git-branch, object-model]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Rebase vs. merge
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What is the key structural difference between `merge` and `rebase`?

**OPTIONS:**
- [x] B: Merge creates a new commit with two parents, preserving both branches' history as it happened; rebase re-plays commits onto a new base, creating entirely new commit objects with new hashes, rewriting history
- [ ] A: Merge and rebase produce identical resulting commit history in every case
- [ ] C: Rebase deletes commits permanently with no way to recover them
- [ ] D: Merge only works on branches with a single commit

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the core distinction: merge preserves actual history via a two-parent commit; rebase creates new commit objects (even if the content looks the same) by replaying changes onto a different base, which is what makes it history-rewriting.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [rebase, merge]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Why rebasing a shared branch is dangerous
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why is rebasing dangerous specifically on a branch other people have already pulled, but safe on a branch only you're working on?

**OPTIONS:**
- [x] B: Rebasing creates new commit objects with different hashes; anyone who already pulled the old commits now has local history that diverges from the rewritten remote history, causing painful conflicts on their next pull
- [ ] A: Rebasing is always unsafe regardless of who else has pulled the branch
- [ ] C: Rebasing only affects the remote repository, never local copies
- [ ] D: This risk only applies to branches with more than 10 commits

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
Since rebase produces new commit objects, anyone else's already-pulled copies of the old commits become orphaned relative to the rewritten history, creating a divergence that has to be manually reconciled — this is exactly what didn't happen with the FDE's declined rebase suggestion in the scenario.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [shared-branch-rebase, history-divergence]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why PR-plus-CI matters more for FDEs
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson argue a PR-plus-CI workflow substitutes for something an FDE often lacks, more than it does for an engineer on a large internal team?

**OPTIONS:**
- [x] B: FDE work is often solo or in a very small on-site group, so an automated, required check provides a structural safety net that doesn't depend on a peer reviewer happening to be available, unlike routine code review on a larger team
- [ ] A: CI checks run faster on FDE projects than on internal team projects
- [ ] C: Large internal teams never use PR-based workflows
- [ ] D: This distinction is not actually meaningful; the lesson treats both cases identically

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The structural safety net argument is specific to the reduced peer-oversight reality of embedded, often-solo FDE work — CI as a required, always-available check substitutes for the review capacity a larger team would otherwise provide.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [PR-workflow, CI, solo-work]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** What MCP adds to an AI coding assistant
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does connecting an AI coding assistant like Claude Code to a customer's ticket tracker via MCP actually enable, in the scenario?

**OPTIONS:**
- [x] B: The assistant can read the actual ticket description directly as additional context while drafting a change, rather than requiring the FDE to manually paste it in
- [ ] A: MCP allows the assistant to merge pull requests without any human review
- [ ] C: MCP is unrelated to AI coding assistants and only applies to n8n workflows
- [ ] D: MCP automatically rewrites Git history to match ticket descriptions

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is MCP's role as a context-connection mechanism, consistent with its use elsewhere in the course — it extends what external context a tool can pull in, here letting the coding assistant reach the ticket tracker directly instead of requiring manual copy-paste.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [MCP, AI-coding-assistant-context]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Why the FDE declined the rebase suggestion
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why did the FDE accept the AI assistant's bug-fix diff but decline its rebase suggestion in the scenario?

**OPTIONS:**
- [x] B: The bug fix was correctly scoped and safe to apply, but the rebase suggestion targeted a branch two other contractors had already pulled, which would have rewritten history they were actively working from — exactly the dangerous case identified earlier in the lesson
- [ ] A: The bug fix itself was actually incorrect and needed to be rejected
- [ ] C: AI-proposed diffs should always be rejected in customer repositories as a blanket policy
- [ ] D: The rebase suggestion was rejected purely because AI tools cannot perform Git operations

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is a direct application of the shared-branch rebase danger from earlier in the lesson — the fix itself was fine, but the specific rebase suggestion targeted a branch with real, current dependents, making it the higher-risk part of the proposal to reject.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [selective-diff-review, rebase-risk]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** AI-proposed diffs and the function-calling analogy
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
How does the lesson connect an AI coding assistant proposing a diff to the function-calling pattern from the Agentic AI Core module?

**OPTIONS:**
- [x] B: Both follow the same "model proposes, you/your code decides" seam — the assistant proposes a diff, but the FDE (not the tool) decides whether and how to actually apply it, just as a function call is proposed but not automatically executed
- [ ] A: The two concepts are unrelated; the comparison is purely coincidental phrasing
- [ ] C: AI coding assistants execute diffs automatically with no review step, unlike function calling
- [ ] D: Function calling and diff proposals both bypass any human decision point

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This mirrors the "model proposes a call, your code decides whether to execute" distinction from the built-in-tools lesson — here applied to code changes, with the human FDE as the decision point instead of application logic.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [propose-vs-execute, cross-module-connection]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Highest-risk category of AI-proposed change
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
According to the lesson, what category of AI-assistant-proposed change deserves the most careful review before acceptance in an unfamiliar customer repository?

**OPTIONS:**
- [x] B: History-rewriting operations (like a rebase on a shared branch) or changes that extend outside the stated scope of the actual task, since these carry consequences well beyond the immediate diff being reviewed
- [ ] A: Any change under 5 lines long, regardless of what it does
- [ ] C: Changes to files with long names, since they're statistically more likely to be important
- [ ] D: All AI-proposed changes carry identical risk and require identical scrutiny

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson specifically calls out history-rewriting git operations and scope-creeping changes as the higher-risk category — not line count or file naming, which don't correlate with actual consequence.

**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [diff-review-checklist, high-risk-changes]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->

---

# LESSON 9

```yaml
lesson_id: fde-foundations-09-testing-pytest-property-based-testing-and-ci
lesson_title: "Testing: pytest, Property-Based Testing & CI"
lesson_order: 9

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: fde-foundations
module_name: "FDE Foundations: Python, Workflow & Delivery"
module_order: 1

difficulty: Medium-Hard
estimated_minutes: 75
content_status: Draft

learning_outcomes:
  - "Use pytest fixtures and parametrize to write concise, non-duplicated test suites."
  - "Explain what property-based testing (Hypothesis) adds beyond example-based tests, and when it's worth the setup cost."
  - "Explain why CI functions as an automated reviewer for FDE work specifically."

created_date: "2026-08-31"
last_updated: "2026-08-31"
author: "Raghuram Balaji"

supplementary_content:
  has_mcq_section: true
  mcq_count: 8
  has_coding_exercises: false
  exercise_count: 0
  has_further_reading: false
  resource_count: 0
```

<!-- CHAPTER_BODY_START -->
# Testing: pytest, Property-Based Testing & CI

## Concepts Covered

pytest fixtures provide reusable setup (and teardown) that multiple tests can depend on by declaring it as a function parameter — a database connection, a populated test object, a temp directory — without every test re-writing that setup inline, and `@pytest.mark.parametrize` runs the same test logic against a list of different input/expected-output pairs, turning what would be several near-duplicate test functions into one function and a data table. Together these keep a growing test suite from becoming its own maintenance burden: adding a new edge case becomes adding one row to a parametrize table, not writing and maintaining a whole new test function.

Example-based tests (including parametrized ones) only check the specific inputs a human thought to write down — which means they only catch a bug if someone happened to anticipate the exact input that triggers it. Property-based testing, via the Hypothesis library, inverts this: instead of specifying example inputs, you specify a *property* that should hold for all valid inputs ("parsing then re-serializing a record should produce the original record," "this function should never raise for any string input, only return an error result"), and Hypothesis generates a wide range of inputs — including edge cases a human wouldn't think to write by hand, like empty strings, unicode, extremely long inputs, or numbers at type boundaries — searching specifically for a case that breaks the property. When it finds one, it automatically shrinks the failing input down to the smallest example that still reproduces the failure, which is usually far more useful for debugging than the large, complex input it originally generated. This is particularly valuable for FDE work parsing real, messy customer data, where the actual range of inputs in production is exactly the kind of thing a human wouldn't fully anticipate by hand-writing examples.

Continuous integration — running the full test suite automatically on every push or pull request via GitHub Actions or similar — converts "the tests pass on my machine" into "the tests pass, verified by an environment nobody's local machine quirks can accidentally influence," and gates merging on that result rather than trusting a human to remember to run tests before merging. Combined with the PR-based workflow from the previous lesson, CI is the automated component of the review substitute an FDE, often working with less peer oversight, specifically benefits from — it doesn't care whether a human reviewer was available, doesn't get tired, and catches a regression the moment it's introduced rather than whenever someone happens to notice broken behavior in production.

## Practical Backend Scenario

The CSV-parsing pipeline from an earlier lesson has a solid example-based pytest suite — it correctly handles a normal row, a row with a missing optional field, and a malformed row missing a required field, all passing. In production against a customer's real export, it crashes on a row containing a null byte embedded in a text field — an input none of the hand-written examples anticipated, because no one writing example-based tests thought to include that specific case. Adding a Hypothesis-based property test — "parsing any string input, valid or garbage, should either return a valid record or a clear validation error, and should never raise an unhandled exception" — run against Hypothesis's text-generation strategies (which deliberately include null bytes, control characters, and other edge-case unicode) would have generated exactly this failing input during development and shrunk it down to a minimal reproducing case, catching the bug in CI before the customer's real file ever hit it in production.

## Practice Loop

1. Write a pytest fixture that sets up a small reusable object (e.g. a populated in-memory list of records) and use it in at least two separate test functions.
2. Take three near-duplicate test functions testing the same logic against different inputs and expected outputs, and collapse them into one parametrized test.
3. Install Hypothesis and write a property-based test for a small string-processing function you write yourself (e.g. a function that should never crash regardless of input, only return a success or error result), and let Hypothesis search for a failing case.
4. If Hypothesis finds a failing input, inspect the shrunk minimal example it reports and compare how much faster it is to understand than the full randomly-generated input would have been.
5. Set up a GitHub Actions workflow that runs your pytest suite (including the property-based test) on every push, and confirm a deliberately broken commit is correctly flagged as failing before you fix it.

## Evidence of Understanding

You can use pytest fixtures and `parametrize` to write a concise test suite without duplicated setup or near-duplicate test functions. You can explain what property-based testing checks that example-based testing cannot (arbitrary inputs across a specified property, not just hand-picked examples) and why Hypothesis's automatic shrinking of failing inputs is valuable for debugging. You can explain concretely why CI functions as an automated reviewer specifically valuable to FDE work, connecting it to the reduced-peer-oversight reasoning from the Git/GitHub lesson.

## Suggested Extension

Take the record-validation property test from the practice loop and add a second property specifically checking a round-trip invariant (parse a record, serialize it back out, parse the serialized output again, and assert the two parsed records are equal) — and explain what class of bug a round-trip property test catches that a simple "doesn't crash" property does not.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** What parametrize solves
**DIFFICULTY:** Easy
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What problem does `@pytest.mark.parametrize` solve compared to writing several near-duplicate test functions?

**OPTIONS:**
- [x] B: It collapses near-duplicate test logic into one function and a data table of input/expected-output pairs, so adding a new case is adding one row instead of a whole new function
- [ ] A: It makes tests run in parallel automatically
- [ ] C: It removes the need for assertions in test functions
- [ ] D: It is required for pytest to discover any test at all

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Parametrize's value is reducing duplication — the test logic is written once, and new cases are added as data, keeping the suite maintainable as it grows.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [pytest-parametrize, test-duplication]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Property-based vs. example-based testing
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What is the fundamental difference between property-based testing and example-based testing?

**OPTIONS:**
- [x] B: Property-based testing specifies a property that should hold for all valid inputs and lets the framework generate a wide range of inputs to search for violations, rather than checking only specific, hand-picked example inputs
- [ ] A: Property-based tests run faster than example-based tests in every case
- [ ] C: Property-based testing replaces the need to write any test assertions
- [ ] D: There is no meaningful difference; the two terms describe the same technique

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The core inversion is specifying a property instead of examples — the framework then generates inputs (including ones a human wouldn't think to write) to search for a case that breaks the stated property.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [property-based-testing, hypothesis]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Why shrinking matters
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why is Hypothesis's automatic shrinking of a failing input to its minimal reproducing case valuable?

**OPTIONS:**
- [x] B: A large, complex randomly-generated failing input is harder to debug than the smallest input that still triggers the same failure — shrinking makes the actual root cause easier to see
- [ ] A: Shrinking makes the test suite run faster overall
- [ ] C: Shrinking is required for Hypothesis to detect a failure at all
- [ ] D: Shrinking converts a property-based test back into an example-based test

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The debugging value comes specifically from reducing a large, possibly confusing generated input down to the minimal case that still fails — which is far easier to reason about than the original.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [hypothesis-shrinking, debugging]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Diagnosing the null-byte production crash
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why did the CSV pipeline's solid example-based test suite fail to catch the null-byte crash before it hit production?

**OPTIONS:**
- [x] B: Example-based tests only check inputs a human specifically thought to write down, and no one writing the hand-picked examples anticipated an embedded null byte, so the suite never exercised that case
- [ ] A: The example-based tests were poorly written and contained bugs of their own
- [ ] C: pytest cannot detect crashes under any circumstances
- [ ] D: The null byte issue was unrelated to testing and was actually a deployment configuration problem

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is exactly the coverage gap property-based testing is designed to close — example-based tests are bounded by human imagination about what inputs to write, and real-world data routinely exceeds that imagination.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [example-based-gap, production-crash]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** How the Hypothesis property would have caught the bug
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why would a Hypothesis property test ("parsing any string should never raise an unhandled exception, only return a record or a clear validation error") have caught the null-byte bug during development?

**OPTIONS:**
- [x] B: Hypothesis's text-generation strategies deliberately include edge cases like null bytes and control characters, so the property test would generate exactly this kind of input while searching for a violation, catching it in CI before it reached production
- [ ] A: This property test would not have caught the bug; only manual testing against the real customer file could have
- [ ] C: Hypothesis only tests numeric inputs, not string inputs
- [ ] D: Property-based tests cannot detect unhandled exceptions

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the direct payoff of property-based testing over example-based testing — Hypothesis's generation strategies are specifically built to explore edge cases like this without a human having to anticipate them individually.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [hypothesis-strategies, bug-prevention]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** CI as an automated reviewer
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
How does this lesson's framing of CI connect to the reduced-peer-oversight argument from the Git/GitHub lesson?

**OPTIONS:**
- [x] B: CI is the automated component of the same review substitute — it doesn't depend on a human reviewer's availability, catching regressions the moment they're introduced, which specifically benefits FDE work that often has less routine peer review than a larger team
- [ ] A: CI and code review serve completely unrelated purposes with no meaningful connection
- [ ] C: CI replaces the need for any human review of any kind, ever
- [ ] D: This connection only applies to teams larger than 10 engineers

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
CI gating merge is the automated half of the same structural-safety-net argument made about PR review in the previous lesson — together they substitute for the peer-oversight capacity a small or solo FDE engagement may lack.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [CI, cross-lesson-connection]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** When property-based testing is worth the setup cost
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Based on the lesson's framing, for which kind of FDE code is property-based testing most worth its extra setup effort compared to example-based tests alone?

**OPTIONS:**
- [x] B: Code parsing real, messy customer data, where the actual range of production inputs is exactly the kind of thing a human wouldn't fully anticipate by hand-writing examples
- [ ] A: A fixed configuration constant that never changes
- [ ] C: Code with no external inputs of any kind
- [ ] D: Property-based testing provides equal value for every kind of code, with no meaningful difference in worthwhileness

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson's central justification for property-based testing's extra effort is specifically about input-parsing code exposed to unpredictable real-world data — exactly the CSV-parsing scenario used to illustrate it.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [property-testing-worthwhileness, real-world-data]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** What a round-trip property catches
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What class of bug does a round-trip property test (parse, serialize, re-parse, compare) catch that a simple "doesn't crash" property does not?

**OPTIONS:**
- [x] B: Silent data corruption or information loss during parsing/serialization — cases where the code runs without error but produces a subtly different result than the original, which a "doesn't crash" check would never flag since no exception occurs
- [ ] A: Round-trip properties and "doesn't crash" properties catch exactly the same bugs
- [ ] C: Round-trip properties can only be used with numeric data types
- [ ] D: Round-trip properties are strictly a performance optimization, not a correctness check

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
A "doesn't crash" property only guards against exceptions; a round-trip equality check specifically guards against silent correctness bugs where parsing succeeds but subtly loses or alters information — a materially different and often more insidious failure mode.

**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [round-trip-property, silent-corruption]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->

---

# LESSON 10

```yaml
lesson_id: fde-foundations-10-software-engineering-best-practices-solid-hexagonal-architecture
lesson_title: "Software Engineering Best Practices (SOLID, Hexagonal Architecture)"
lesson_order: 10

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: fde-foundations
module_name: "FDE Foundations: Python, Workflow & Delivery"
module_order: 1

difficulty: Medium-Hard
estimated_minutes: 75
content_status: Draft

learning_outcomes:
  - "Explain the SOLID principles practically, with emphasis on Dependency Inversion's specific relevance to FDE work."
  - "Structure code using hexagonal architecture (ports and adapters) so external systems can be swapped without touching business logic."
  - "Recognize when a prototype's shortcuts should become a proper port/adapter boundary as an engagement matures."

created_date: "2026-08-31"
last_updated: "2026-08-31"
author: "Raghuram Balaji"

supplementary_content:
  has_mcq_section: true
  mcq_count: 8
  has_coding_exercises: false
  exercise_count: 0
  has_further_reading: false
  resource_count: 0
```

<!-- CHAPTER_BODY_START -->
# Software Engineering Best Practices (SOLID, Hexagonal Architecture)

## Concepts Covered

SOLID's five principles matter differently depending on context, and for FDE work specifically, Dependency Inversion carries the most practical weight: depend on an abstraction (an interface, a Python `Protocol`) rather than a concrete implementation, so the concrete implementation can be swapped without changing the code that depends on it. This matters more for an FDE than for someone building a stable internal system because FDE scope changes rapidly and unpredictably mid-engagement — a prototype often starts against a local file or a mocked data source simply because the customer's real system isn't accessible yet, and if business logic is written directly against that concrete source, "the real system just became available" turns into a rewrite instead of a swap. Single Responsibility (a module changes for one reason, not several unrelated ones) and Open/Closed (new behavior extends through a new implementation of an existing abstraction, rather than modifying existing, already-working code) both reinforce the same practical outcome: code structured this way tolerates the kind of rapid, discovery-driven scope change that's normal in FDE engagements, rather than requiring an increasingly risky rewrite every time the picture changes.

Hexagonal architecture (ports and adapters) gives this principle a concrete, teachable shape: business logic sits at the center of the design with no knowledge of any specific external system, "ports" are the interfaces that logic defines for what it needs (a `DeviceRepository` port defining `get_device(id)` and `save_device(device)`, with no mention of SQLite, an HTTP API, or any specific technology), and "adapters" are the concrete implementations of those ports against actual outside systems (a `SqliteDeviceRepository`, later a `CustomerApiDeviceRepository`). The core logic only ever talks to the port's interface, never to a specific adapter directly, which is what makes an adapter swap possible without touching the logic at all — the business rules were never coupled to *how* device records are actually stored or fetched, only to *what* operations are available.

The judgment call this unlocks specifically for FDE work: when a customer's real system isn't accessible yet (a common week-one reality), building against a lightweight local adapter (a SQLite file, an in-memory mock) instead of blocking on access is the right move precisely because a hexagonal structure means that decision is cheap to reverse later — the local adapter gets replaced with a real one once access exists, and the business logic that was built and validated against the mock never has to change. Skipping this structure and coding directly against the mock (SQLite calls sprinkled through business logic) makes the same later swap expensive and risky, turning what should be "write one new adapter" into "carefully find and rewrite every place the mock leaked into the logic."

## Practical Backend Scenario

The provisioning-assistant tool from an earlier lesson needed a "device record" data source, but the customer's real device database wasn't accessible during week one of the engagement. Structured hexagonally from the start, the FDE defined a `DeviceRepository` port (an abstract interface with `get_device` and `update_device` methods) and built a `SqliteDeviceRepository` adapter backed by a local file populated with realistic test data, letting the provisioning logic be built and validated immediately without waiting on customer access. When the customer's real device API became available in week three, the fix was writing one new `CustomerApiDeviceRepository` adapter implementing the same port against the real API and swapping which adapter gets instantiated at startup — the provisioning logic itself, already tested against the mock, needed zero changes, because it had never referenced SQLite or any storage detail directly, only the port's interface.

## Practice Loop

1. Define a `DeviceRepository` abstract interface (a Python `Protocol` or `ABC`) with `get_device(id)` and `update_device(device)` methods, with no reference to any specific storage technology.
2. Implement a `SqliteDeviceRepository` adapter satisfying that interface, backed by a local SQLite file with a few test records.
3. Write the provisioning logic (or a simplified version of it) so it only depends on the `DeviceRepository` interface, never on SQLite specifics directly — pass the concrete adapter in via constructor injection, not imported and instantiated inside the logic itself.
4. Write a second adapter, `InMemoryDeviceRepository`, satisfying the same interface with no real storage at all (just a Python dict), and confirm you can swap it in for tests without changing a single line of the provisioning logic.
5. Write a one-paragraph explanation of what would have gone wrong when the real customer API became available in week three, if the provisioning logic had called SQLite directly instead of going through the `DeviceRepository` port.

## Evidence of Understanding

You can explain Dependency Inversion practically (depend on abstractions, not concrete implementations) and why it matters more for FDE work's fast-changing scope than for a stable internal system. You can structure code using a port (an interface defining what business logic needs) and an adapter (a concrete implementation against a specific external system), and explain why business logic should only ever reference the port. You can identify, in a real scenario, when building against a lightweight local adapter instead of blocking on customer access is the right early-engagement move, and why that decision stays cheap to reverse only if the hexagonal structure is in place from the start.

## Suggested Extension

Add a third adapter, `CachedDeviceRepository`, that wraps any other `DeviceRepository` implementation and adds a simple in-memory cache in front of it — demonstrating that adapters themselves can be composed (an adapter wrapping another adapter, both satisfying the same port) without the business logic ever needing to know a cache was added.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Why Dependency Inversion matters most for FDE work
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson single out Dependency Inversion as carrying the most practical weight specifically for FDE work?

**OPTIONS:**
- [x] B: FDE scope changes rapidly and unpredictably mid-engagement, and if business logic depends directly on a concrete implementation rather than an abstraction, a change in what's available (like real customer system access arriving later) forces a rewrite instead of a swap
- [ ] A: The other four SOLID principles are irrelevant to any software engineering context
- [ ] C: Dependency Inversion is the only SOLID principle that applies to Python specifically
- [ ] D: This distinction is arbitrary and has no real justification

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The practical argument is specific to FDE's rapid-scope-change reality — depending on abstractions is what keeps a later change in the concrete implementation from forcing a rewrite of the logic that depends on it.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [dependency-inversion, FDE-relevance]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Ports vs. adapters
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In hexagonal architecture, what is the difference between a "port" and an "adapter"?

**OPTIONS:**
- [x] B: A port is the interface business logic defines for what it needs, with no reference to any specific technology; an adapter is a concrete implementation of that interface against an actual external system
- [ ] A: A port and an adapter are two names for the exact same thing
- [ ] C: A port is always a database, and an adapter is always an API
- [ ] D: An adapter defines what the logic needs, and a port implements it against a real system

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The port is the abstract contract (what operations are needed); the adapter is the concrete implementation of that contract against a specific real system — getting this direction right is what makes the pattern's naming meaningful, not arbitrary.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [ports-and-adapters, hexagonal-architecture]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** What makes an adapter swap possible
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What specifically makes it possible to swap `SqliteDeviceRepository` for `CustomerApiDeviceRepository` without changing the provisioning logic?

**OPTIONS:**
- [x] B: The provisioning logic only ever calls methods on the `DeviceRepository` port's interface, never referencing SQLite or any storage detail directly, so any adapter satisfying that same interface is interchangeable
- [ ] A: SQLite and the customer's API happen to have identical underlying data formats
- [ ] C: The provisioning logic contains conditional checks for which storage backend is active
- [ ] D: Swapping adapters always requires rewriting the business logic; this scenario is unusual

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The swap works because the logic was never coupled to any adapter's implementation details — it only depends on the port's interface, which both adapters satisfy identically from the logic's point of view.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [adapter-swap, interface-dependency]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** What goes wrong without the port boundary
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What would have gone wrong in week three if the provisioning logic had called SQLite directly instead of going through a `DeviceRepository` port?

**OPTIONS:**
- [x] B: Every place SQLite calls were sprinkled through the business logic would need to be found and rewritten to call the real customer API instead, turning a one-adapter swap into a risky, scattered rewrite of the logic itself
- [ ] A: Nothing different would happen; the outcome would be identical either way
- [ ] C: The customer's real API would automatically become compatible with the SQLite calls
- [ ] D: The provisioning tool would stop working entirely with no possible fix

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the direct cost of skipping the port/adapter boundary — coupling business logic to a concrete implementation means a later swap requires finding and changing every coupled call site instead of writing one new adapter.

**LESSON_CONNECTION:** Practice Loop, Step 5
**KEYWORDS:** [tight-coupling-cost, missing-abstraction]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Why building against a mock in week one was the right call
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why was building against a local SQLite mock in week one, before the customer's real device database was accessible, a sound decision rather than a risky shortcut?

**OPTIONS:**
- [x] B: Because the hexagonal structure made that decision cheap to reverse later — the mock adapter could be swapped for a real one without touching the already-validated business logic, so building against the mock didn't lock in any real risk
- [ ] A: Because the customer's real database was never actually going to be needed
- [ ] C: Because SQLite is technically identical to any production database system
- [ ] D: Because mocks are always safe regardless of how the code is structured

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The soundness of the decision depends entirely on the structure being in place — the same decision without the port/adapter boundary would have been a real risk, since it would have locked business logic to the mock's specifics.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [early-mock-decision, reversibility]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Single Responsibility and Open/Closed's shared outcome
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What shared practical outcome do Single Responsibility and Open/Closed both reinforce, according to the lesson?

**OPTIONS:**
- [x] B: Code structured around these principles tolerates rapid, discovery-driven scope change without requiring an increasingly risky rewrite each time the picture changes
- [ ] A: They guarantee code runs faster at scale
- [ ] C: They eliminate the need for any testing
- [ ] D: They are only relevant to object-oriented languages, not Python specifically

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson frames all three principles it discusses (SRP, Open/Closed, Dependency Inversion) as reinforcing the same practical outcome — tolerance for the kind of scope change that's normal in FDE engagements, not an abstract design purity goal.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [SRP, open-closed, scope-tolerance]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Constructor injection vs. internal instantiation
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the practice loop specify passing the concrete adapter in via constructor injection, rather than having the provisioning logic import and instantiate `SqliteDeviceRepository` internally?

**OPTIONS:**
- [x] B: Instantiating a concrete adapter internally would re-couple the logic to that specific implementation, defeating the purpose of depending only on the port's interface — injection keeps the logic agnostic to which adapter is actually supplied
- [ ] A: Constructor injection is required by Python syntax for any class to function
- [ ] C: There is no practical difference between the two approaches
- [ ] D: Internal instantiation is always faster at runtime than injection

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
If the logic imports and constructs the concrete adapter itself, it's coupled to that specific class regardless of the interface existing — injection is what actually keeps the swap possible, echoing the same dependency-injection principle from the Facade pattern discussion in other parts of this platform.

**LESSON_CONNECTION:** Practice Loop, Step 3
**KEYWORDS:** [constructor-injection, coupling]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Composing adapters
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why can a `CachedDeviceRepository` wrap another `DeviceRepository` adapter and add caching, without the business logic ever needing to know a cache was introduced?

**OPTIONS:**
- [x] B: `CachedDeviceRepository` itself satisfies the same `DeviceRepository` port as any other adapter, so from the logic's perspective it's just another interchangeable implementation — the fact that it happens to wrap and delegate to a different adapter internally is invisible to the logic
- [ ] A: Caching requires modifying the business logic directly to check a cache before calling the repository
- [ ] C: This kind of composition is not actually possible in a hexagonal architecture
- [ ] D: `CachedDeviceRepository` must be a subclass of the business logic itself to function

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
Because the port defines the contract and any adapter satisfying it is interchangeable to the logic, an adapter is free to be implemented however it likes internally — including wrapping and delegating to another adapter — without that internal detail ever surfacing to the business logic depending on the port.

**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [adapter-composition, cache-wrapping]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->

---

# LESSON 11

```yaml
lesson_id: fde-foundations-11-linux-shell-and-scripting-for-fdes
lesson_title: "Linux, Shell & Scripting for FDEs"
lesson_order: 11

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: fde-foundations
module_name: "FDE Foundations: Python, Workflow & Delivery"
module_order: 1

difficulty: Intermediate
estimated_minutes: 60
content_status: Draft

learning_outcomes:
  - "Use pipes and composable single-purpose commands (grep, sed, awk) for fast log/data triage without writing a script."
  - "Inspect service status and logs on an unfamiliar Linux host using ps, systemd, and journalctl."
  - "Write a defensive shell script (set -euo pipefail, proper quoting) and judge when shell is the right tool versus Python."

created_date: "2026-08-31"
last_updated: "2026-08-31"
author: "Raghuram Balaji"

supplementary_content:
  has_mcq_section: true
  mcq_count: 8
  has_coding_exercises: false
  exercise_count: 0
  has_further_reading: false
  resource_count: 0
```

<!-- CHAPTER_BODY_START -->
# Linux, Shell & Scripting for FDEs

## Concepts Covered

An FDE frequently operates on infrastructure they didn't set up, without a full IDE, and sometimes without the ability to install anything new — which makes shell fluency a baseline requirement, not a nice-to-have. The Unix philosophy of small, single-purpose commands composed via pipes (`grep`, `sed`, `awk`, `sort`, `uniq`, each doing one thing well, chained with `|` so one command's output becomes the next's input) is directly useful for exactly the kind of fast triage an FDE needs: filtering a huge log file down to relevant lines with `grep`, extracting or reshaping specific fields with `awk`, without writing and saving a script for a question you'll only ever ask once. This is the same composability principle from the generators/iterators lesson, expressed at the shell level instead of in Python — small pieces, each independently understandable, chained together to answer a specific question.

Diagnosing a running system requires knowing where to look: `ps` (and `ps aux` specifically) shows currently running processes, useful for confirming whether a service is actually running or checking what's consuming resources; on a `systemd`-managed host, `systemctl status <service>` shows a service's current state and recent log excerpts directly, and `journalctl -u <service>` pulls that service's full structured log history, filterable by time range (`--since`) — this is frequently the fastest path to an answer on a customer's server where there's no access to whatever internal monitoring dashboard the customer's own team relies on. Permissions matter for a specific reason beyond correctness: a customer's production server is not the place to reach for `chmod 777` to make a permission error go away, because that grants far more access than the actual problem requires and leaves a lasting security gap — the same least-privilege reasoning from the tool-permission and privilege-separation lessons applies directly here, just at the level of filesystem permissions instead of an agent's tool access.

Writing a shell script rather than issuing one-off commands is the right move once a sequence needs to be repeated, or once a mistake in it would be costly — and a script intended for a customer's production system should be written defensively: `set -euo pipefail` at the top of a bash script makes it exit immediately on any command failure (`-e`), on any reference to an unset variable (`-u`), and on a failure anywhere in a pipeline rather than only the last command (`pipefail`) — without these, a script can silently continue past a failed step and do real damage based on incomplete or wrong state, exactly the kind of failure mode that's invisible until it's already caused a problem. Quoting variables (`"$variable"` rather than bare `$variable`) prevents word-splitting and glob-expansion surprises when a variable's value contains spaces or special characters — a common, sneaky source of shell script bugs. The judgment call between reaching for shell versus Python: a quick, one-off diagnostic question (filter this log, count these occurrences) is shell's natural territory; anything involving real branching logic, structured error handling, or that will be run more than a couple of times and needs to be maintained belongs in Python, where the tooling from earlier lessons (testing, typing, structured logging) actually applies.

## Practical Backend Scenario

An FDE SSHes into a customer's production server at 2am to investigate a stalled background job, with no IDE, no local dev environment, and no access to the customer's internal monitoring stack. `systemctl status sync-worker` shows the service is technically still running but hasn't logged anything in 40 minutes — a `journalctl -u sync-worker --since "1 hour ago"` pulled and piped through `grep -i error` immediately surfaces a repeated connection-timeout error the service has been silently retrying without giving up, explaining the stall. Rather than a fragile one-line `systemctl restart sync-worker` that would silently mask the underlying timeout and might fail partway if a cleanup step is needed first, the FDE writes a small defensive script — `set -euo pipefail` at the top, each step (stop the service, clear a specific stale lock file, restart the service, confirm it's actually accepting connections) checked explicitly, exiting loudly at the first failure rather than plowing ahead with a corrupted intermediate state — because a one-off command run under time pressure at 2am is exactly the situation where a silent partial failure does the most damage.

## Practice Loop

1. Given a sample log file with a mix of normal and error lines, use `grep` to filter to just error lines, then pipe that through `awk` to extract just the timestamp and error-code fields.
2. Practice reading `ps aux` output and identifying a specific process by name; separately, if you have access to a systemd-managed Linux system (or a container running one), use `systemctl status` and `journalctl -u` on a real service to see its current state and recent logs.
3. Write a shell script without `set -euo pipefail` that has a deliberate failure in its second of three steps, run it, and observe that it silently continues to the third step despite the second one failing; add `set -euo pipefail` and confirm it now stops immediately at the failure.
4. Write a small script that takes a filename as an argument and demonstrate the difference between using `$1` unquoted versus `"$1"` quoted, using a filename that contains a space, to see the quoting bug directly.
5. Take the 2am scenario's restart procedure (stop, clear lock file, restart, confirm healthy) and write it as a defensive script with explicit checks at each step, rather than a single chained one-liner.

## Evidence of Understanding

You can compose `grep`, `sed`, and `awk` via pipes to answer a specific ad-hoc question about a log file without writing a saved script. You can use `ps`, `systemctl status`, and `journalctl` to diagnose a service's current state and recent history on an unfamiliar Linux host. You can write a defensive shell script using `set -euo pipefail` and proper variable quoting, and you can judge correctly when a task belongs in a quick shell one-liner versus when it should become a properly tested, typed Python script.

## Suggested Extension

Extend the 2am restart script to log its own actions (each step, and whether it succeeded) to a file as it runs — connecting this lesson's defensive-scripting discipline back to the structured-logging principle from earlier in this module, so that if the script is run again later by someone else entirely (a customer's own on-call engineer, per the "enable" principle from the first lesson in this module), there's a clear record of exactly what it did and when.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Why shell fluency is a baseline for FDEs
**DIFFICULTY:** Easy
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson describe shell fluency as a baseline requirement rather than a nice-to-have for FDE work?

**OPTIONS:**
- [x] B: An FDE frequently operates on infrastructure they didn't set up, often without a full IDE and sometimes without the ability to install new tools, making shell the tool that's reliably already available
- [ ] A: Shell scripts always run faster than equivalent Python programs
- [ ] C: Customers require every FDE to use shell exclusively by contractual policy
- [ ] D: IDEs are technically incompatible with Linux servers

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The justification is about availability and constraint, not raw performance — shell is what's reliably present on unfamiliar infrastructure the FDE didn't set up and may not be able to modify.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [shell-fluency, unfamiliar-infrastructure]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** journalctl vs. ps
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
You need to see the last hour of a specific systemd-managed service's log history to look for errors. Which command is the right tool?

**OPTIONS:**
- [x] B: `journalctl -u <service> --since "1 hour ago"`, since `journalctl` pulls a service's full structured log history filterable by time range
- [ ] A: `ps aux`, since it shows all currently running processes
- [ ] C: `systemctl status <service>` alone, since it shows the complete log history with no time limit
- [ ] D: `chmod 777` on the service's log directory

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
`ps` shows current process state, not log history; `systemctl status` shows only a brief recent excerpt, not a full time-ranged query. `journalctl -u` with `--since` is specifically built for pulling filtered log history.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [journalctl, systemd-diagnostics]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Why chmod 777 is a red flag
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson single out `chmod 777` as a red flag on a customer's production server rather than an acceptable quick fix for a permission error?

**OPTIONS:**
- [x] B: It grants far more access than the actual problem requires, leaving a lasting security gap — the same least-privilege reasoning that applies to agent tool permissions applies to filesystem permissions
- [ ] A: `chmod 777` is technically invalid syntax on most Linux systems
- [ ] C: Permission errors can never actually be fixed with `chmod`
- [ ] D: `chmod 777` only affects files, never directories, making it ineffective for most fixes

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is a direct application of least-privilege thinking from earlier security-focused lessons, just applied to filesystem permissions instead of agent tool access — granting maximal access to fix a narrow problem is the anti-pattern being flagged.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [least-privilege, chmod-777]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** What set -euo pipefail does
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does `set -euo pipefail` do at the top of a bash script?

**OPTIONS:**
- [x] B: Exits immediately on any command failure, on any reference to an unset variable, and on a failure anywhere in a pipeline (not just the last command) — preventing the script from silently continuing past a failed step
- [ ] A: Makes the script run faster by skipping error checks
- [ ] C: Automatically fixes any errors the script encounters
- [ ] D: Suppresses all output from the script for cleaner logs

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
Each flag closes a specific silent-failure gap: `-e` for command failures, `-u` for unset variables, `pipefail` for failures buried in the middle of a pipeline that would otherwise be masked by the last command's exit status.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [set-euo-pipefail, defensive-scripting]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Why the FDE avoided a one-line restart
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why did the FDE in the 2am scenario write a defensive multi-step script instead of a single chained `systemctl restart` one-liner?

**OPTIONS:**
- [x] B: A one-off command run under time pressure is exactly the situation where a silent partial failure (e.g. a stale lock file not cleared before restart) does the most damage, so explicit, checked steps that exit loudly on failure were safer than a fragile chained one-liner
- [ ] A: `systemctl restart` is technically incapable of restarting any service
- [ ] B: One-liners are always slower to execute than multi-step scripts
- [ ] D: The customer's server did not support shell scripts of any kind

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The risk being managed is a silent partial failure under time pressure — a defensive, explicitly-checked script surfaces a failure at the exact step it occurs rather than masking it inside a chained command.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [defensive-script-vs-oneliner, time-pressure-risk]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Shell vs. Python judgment call
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
According to the lesson, which task is a better fit for a quick shell command than for a Python script?

**OPTIONS:**
- [x] B: A one-off question like "how many lines in this log file contain a specific error code," asked once and not expected to be repeated or maintained
- [ ] A: A task involving complex branching logic and structured error handling that will run repeatedly in production
- [ ] C: Anything that needs unit tests
- [ ] D: Any task that processes more than 100 lines of input

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The judgment line is about repetition, complexity, and cost of a mistake — a genuinely one-off, simple diagnostic question is shell's natural territory, while anything with real logic or lasting maintenance need belongs in Python where testing and typing tooling actually applies.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [shell-vs-python, tool-selection]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Quoting variables
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson recommend quoting shell variables (`"$variable"`) rather than leaving them bare (`$variable`)?

**OPTIONS:**
- [x] B: Bare variables are subject to word-splitting and glob-expansion, which can cause surprising bugs when the variable's actual value contains spaces or special characters
- [ ] A: Quoting is purely a stylistic convention with no functional effect
- [ ] C: Bare variables are faster to type but always crash the script
- [ ] D: Quoting is only required for variables holding numeric values

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
Unquoted variables undergo word-splitting and glob expansion by the shell, which is a real, common source of subtle bugs when a value contains spaces or shell-special characters — quoting prevents this.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [variable-quoting, word-splitting]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Connecting script logging to the "enable" principle
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the suggested extension connect adding logging to the restart script back to the "enable" step from the FDE-role lesson?

**OPTIONS:**
- [x] B: A script that logs its own actions leaves a clear record for someone else — like the customer's own on-call engineer — who runs it later without the FDE present, which is exactly the capability-transfer goal "enable" describes
- [ ] A: Logging has no relationship to enablement; the connection is incorrect
- [ ] C: Scripts without logging cannot technically be executed by anyone other than their original author
- [ ] D: This connection only applies if the script fails

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This ties the module's very first lesson (enable — transferring capability to the customer's own team) to a concrete practice here: a script that logs what it did is legible and safely re-runnable by someone who wasn't there when it was written, exactly the enablement goal.

**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [script-logging, enablement-connection]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->

---

# LESSON 12

```yaml
lesson_id: fde-foundations-12-assessment-python-engineering-challenge
lesson_title: "Assessment: Python Engineering Challenge"
lesson_order: 12

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: fde-foundations
module_name: "FDE Foundations: Python, Workflow & Delivery"
module_order: 1

difficulty: Hard
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Integrate toolchain setup, lazy data processing, decorators/context managers, concurrency judgment, validation, structured logging, testing, and hexagonal structure into one small, real deliverable."
  - "Self-assess a solution against an explicit rubric rather than a vague sense of 'it works'."
  - "Reason about the trade-offs behind rubric criteria, not just checklist completion."

created_date: "2026-08-31"
last_updated: "2026-08-31"
author: "Raghuram Balaji"

supplementary_content:
  has_mcq_section: true
  mcq_count: 8
  has_coding_exercises: false
  exercise_count: 0
  has_further_reading: false
  resource_count: 0
```

<!-- CHAPTER_BODY_START -->
# Assessment: Python Engineering Challenge

## Concepts Covered

This assessment is a self-check, not a new mechanism — its purpose is confirming that the individual tools from this module's eleven lessons (toolchain setup, lazy iteration, closures/decorators/context managers, concurrency judgment, Pydantic validation, structured logging, git/testing workflow, and hexagonal structure) compose correctly into one small, coherent, real deliverable, the way they'd actually need to on a real engagement rather than in eleven separate isolated exercises. A rubric-driven self-assessment, evaluated against explicit, checkable criteria rather than a vague "does this feel done," mirrors the discipline from the problem-discovery lesson: a falsifiable bar defined before you call something finished, not a retroactively-adjusted sense of completion.

**The challenge brief:** build a small command-line tool that ingests a large (simulated) customer log file and produces a structured summary report. Specifically: (1) the tool reads log lines lazily via a generator, never loading the full file into memory at once; (2) each parsed line is validated into a Pydantic model, with malformed lines routed to a separate error-count rather than crashing the run; (3) the tool's core logic (parsing rules, summary calculation) is structured behind a `LogSource` port with at least two adapters — a real file-reading adapter and an in-memory adapter usable in tests — so the summarization logic never references file I/O directly; (4) progress and any validation failures are emitted as structured log events, not print statements; (5) the project has a `pyproject.toml`-based, `uv`-managed, reproducible environment with a lockfile; (6) the test suite includes both example-based pytest tests and at least one Hypothesis property-based test covering the line-parsing logic; (7) the whole thing is developed on a feature branch with at least one PR, gated by a CI check that runs the test suite.

**The rubric**, in order of weight: **Functional correctness** — does the tool produce a correct summary against a known test log file, including correctly routing malformed lines to the error count instead of crashing. **Structural soundness** — is the `LogSource` port genuinely respected (does swapping the in-memory adapter for the file adapter require zero changes to the summarization logic), or did implementation details leak through. **Test quality** — do the tests, especially the property-based one, actually exercise a meaningful property (not a trivial always-true assertion), and would they have caught a real regression if one were introduced. **Operational hygiene** — is the environment genuinely reproducible from a clean clone plus the lockfile, are logs structured and would they actually help someone else diagnose an issue, does CI genuinely gate the PR rather than being decorative.

## Practical Backend Scenario

This assessment doesn't need a separate scenario — it *is* the scenario, deliberately built to be small enough to complete in one sitting but real enough that skipping any single rubric item (skipping the Hypothesis test, coding directly against file I/O instead of through the `LogSource` port, using print statements instead of structured logs) produces a noticeably worse, less defensible result rather than a merely "less polished" one. That gap between "technically works" and "actually meets the rubric" is deliberate: it's the same gap between a demo that happens to work once and a slice that's genuinely validated, instrumented, and enable-able, which is the standard the FDE-role lesson set at the very start of this module.

## Practice Loop

1. Build the tool against the brief above, starting with the `LogSource` port and an `InMemoryLogSource` adapter so the summarization logic can be developed and tested before any real file-reading code exists at all.
2. Add a `FileLogSource` adapter once the logic is working against the in-memory version, and confirm the summarization logic required zero changes.
3. Write the Hypothesis property test for line parsing — a good candidate property: "for any string input, parsing either returns a valid record or increments the error count, and never raises an unhandled exception" — and let it run against generated inputs, including deliberately malformed ones.
4. Set up the `pyproject.toml` + `uv.lock` reproducible environment, delete your local environment, and rebuild it from the lockfile alone to confirm reproducibility, exactly as practiced in the toolchain lesson.
5. Push to a feature branch, open a PR with a CI check running your test suite, and self-score your own solution against all four rubric categories before merging — writing down, specifically, which category you'd score lowest and why.

## Evidence of Understanding

You can build a small, real, multi-file Python project that composes lazy iteration, validation, structured logging, hexagonal structure, and tested code into one coherent tool, not eleven disconnected snippets. You can evaluate your own work against an explicit rubric rather than a vague sense of completion, and you can identify specifically which rubric category is weakest in a given solution rather than giving yourself a uniform, non-diagnostic score. You understand why skipping any single rubric item (structure, tests, logging, reproducibility) produces a materially worse deliverable, not just a less polished one.

## Suggested Extension

Have a peer (or, absent one, re-review your own solution after a day's gap) score your solution against the same rubric independently, and compare scores — a significant disagreement on any category is worth investigating, since it usually means the rubric criterion was more ambiguous in practice than it seemed when you wrote the code.

## Self-Assessment Questions (rubric judgment, not new material)

<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Purpose of this assessment
**DIFFICULTY:** Easy
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What is the actual purpose of this assessment, according to the lesson?

**OPTIONS:**
- [x] B: Confirming that the module's individual tools (lazy iteration, validation, logging, hexagonal structure, testing) compose correctly into one coherent deliverable, the way they'd need to on a real engagement — not testing any single new mechanism
- [ ] A: Teaching an entirely new Python library not covered elsewhere in the module
- [ ] C: Testing typing speed under a strict time limit
- [ ] D: Determining whether the learner should use Python or a different language going forward

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This lesson is explicitly a composition check, not new content — its value is in proving the module's separate lessons actually integrate, which is a distinct skill from executing each one in isolation.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [assessment-purpose, integration]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** How malformed lines should be handled
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the challenge brief, what should happen when the tool encounters a malformed log line?

**OPTIONS:**
- [x] B: The malformed line should be routed to a separate error count, not crash the entire run
- [ ] A: The entire tool should stop and exit immediately on the first malformed line
- [ ] C: Malformed lines should be silently discarded with no record of how many were skipped
- [ ] D: Malformed lines should be automatically corrected and processed as if valid

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The brief is explicit: malformed input increments an error count rather than crashing the run or being silently dropped — a design decision that mirrors the earlier lesson's Hypothesis property about never raising unhandled exceptions on arbitrary input.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1 (challenge brief)
**KEYWORDS:** [malformed-input-handling, error-count]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Checking structural soundness
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
How does the rubric's "structural soundness" category propose checking whether the `LogSource` port is genuinely respected, rather than just nominally present?

**OPTIONS:**
- [x] B: Swapping the in-memory adapter for the file adapter should require zero changes to the summarization logic — if it doesn't, implementation details leaked through the supposed abstraction
- [ ] A: Counting the number of lines of code in the `LogSource` interface definition
- [ ] C: Checking whether the interface is named with the word "Port" in it
- [ ] D: Structural soundness cannot actually be verified and is a purely subjective judgment

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is a concrete, checkable test rather than a subjective judgment — it directly verifies the hexagonal-architecture claim from the earlier lesson: if swapping adapters requires touching the logic, the port wasn't actually respected regardless of what the code looks like on the surface.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1 (rubric)
**KEYWORDS:** [structural-soundness, verifiable-rubric]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** What makes a Hypothesis test count for "test quality"
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
According to the rubric's "test quality" criterion, what distinguishes a good property-based test from a weak one that technically satisfies the requirement?

**OPTIONS:**
- [x] B: A good property test exercises a meaningful property that would actually catch a real regression if one were introduced, not a trivial always-true assertion that technically runs Hypothesis but proves nothing
- [ ] A: A good property-based test must contain at least 100 lines of code
- [ ] C: Any test using the Hypothesis library automatically counts as high quality regardless of what it checks
- [ ] D: Test quality is measured purely by how long the test suite takes to run

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The rubric explicitly guards against gaming the checklist — merely having a Hypothesis test present isn't the bar; the test has to actually check something meaningful enough to catch a real regression.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1 (rubric)
**KEYWORDS:** [test-quality, meaningful-properties]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Why build the InMemoryLogSource adapter first
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the practice loop suggest building the `InMemoryLogSource` adapter before the `FileLogSource` adapter?

**OPTIONS:**
- [x] B: It lets the summarization logic be developed and tested immediately, without any real file-reading code needing to exist yet — the same "build against a lightweight local adapter first" pattern from the hexagonal-architecture lesson
- [ ] A: In-memory adapters are always required to be built before file adapters by Python convention
- [ ] C: File-reading code is technically impossible to write in Python
- [ ] D: This ordering has no particular rationale; either order works identically

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This directly reuses the earlier lesson's pattern — building against a fast, simple local adapter first lets the core logic get built and validated before the (often slower or less available) real adapter is ready.

**LESSON_CONNECTION:** Practice Loop, Step 1
**KEYWORDS:** [adapter-build-order, hexagonal-reuse]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** What "operational hygiene" checks
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does the rubric's "operational hygiene" category evaluate?

**OPTIONS:**
- [x] B: Whether the environment is genuinely reproducible from a clean clone plus the lockfile, whether logs are structured and actually useful to someone else, and whether CI genuinely gates the PR rather than being decorative
- [ ] A: How many total commits the project has
- [ ] C: Whether the code uses tabs or spaces for indentation
- [ ] D: The total file count in the project directory

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
Operational hygiene pulls together the toolchain, logging, and CI lessons from earlier in the module into one checkable category — genuinely reproducible, genuinely useful logs, and a CI check that actually blocks a broken PR rather than existing only nominally.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1 (rubric)
**KEYWORDS:** [operational-hygiene, rubric-category]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Why skipping a rubric item is worse than "less polished"
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson argue that skipping a rubric item (e.g. coding directly against file I/O instead of through the `LogSource` port) produces a "noticeably worse, less defensible" result rather than merely a less polished one?

**OPTIONS:**
- [x] B: Each rubric item corresponds to a real capability the deliverable loses without it (e.g. skipping the port means losing the ability to swap adapters or test in isolation) — the gap is functional, not cosmetic
- [ ] A: The rubric items are arbitrary stylistic preferences with no functional consequence
- [ ] C: "Less polished" and "less defensible" mean exactly the same thing in this context
- [ ] D: Skipping any rubric item makes the code fail to run entirely

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The rubric items were chosen because each maps to a real, demonstrated capability from earlier lessons (adapter swapping, catching regressions, reproducibility) — skipping one is a functional loss of that capability, not just a stylistic shortfall.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [rubric-item-consequence, functional-vs-cosmetic]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Value of independent re-scoring
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the suggested extension recommend having a peer, or yourself after a day's gap, re-score the solution independently against the same rubric?

**OPTIONS:**
- [x] B: A significant disagreement between the original and independent score on any category usually means that rubric criterion was more ambiguous in practice than it seemed while writing the code, which is worth investigating directly
- [ ] A: Independent re-scoring is purely a formality with no diagnostic value
- [ ] C: A second scoring pass is only useful to catch typos in the code
- [ ] D: Rubric criteria are never ambiguous, so disagreement always indicates a scoring mistake, never an ambiguous criterion

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This echoes the "define success before building" discipline from the problem-discovery lesson — a rubric that produces consistent scores across independent evaluators is doing its job; disagreement is diagnostic of where the rubric (or the solution) was more ambiguous than assumed.

**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [independent-scoring, rubric-ambiguity]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->
