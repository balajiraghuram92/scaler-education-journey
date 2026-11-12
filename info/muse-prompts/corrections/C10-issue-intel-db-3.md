# C10 — `issue-intel/`: one line in the token test helper

C9 worked. Reviewer's run against a real PostgreSQL: **70 passed, 1 failed** (was 68 / 3). `test_token_lifecycle` and the security test now pass.

The last failure comes from a constraint the reviewer's C9 prompt did not mention.

Log: `info/muse-prompts/corrections/round9/issue-intel-db.log`.

Paste everything below this line into Muse Code at the repository root.

---

Work only in `issue-intel/`. One agent. Do not run commands. Do not commit. Do not create or switch branches. Append what you did to `issue-intel/PROGRESS.md` under "C10".

## The one task — `tests/test_tokens.py`, helper `_make_runs`

```
tests/test_tokens.py::test_token_rejections
E  UniqueViolationError: duplicate key value violates unique constraint "uq_runs_ticket_hash_version"
E  DETAIL: Key (ticket_key, content_hash, pipeline_version)=(TOK, 000...000, v0) already exists.
```

`runs` has a unique constraint on `(ticket_key, content_hash, pipeline_version)`. `_make_runs` gives every run the same three values (`"TOK"`, `"0" * 64`, `"v0"`), so the test that creates more than one run fails on the second insert. `test_token_lifecycle` creates one run and passes.

Change inside `_make_runs` only: make `content_hash` unique per run by deriving it from the run id, `content_hash=hashlib.sha256(run_id.encode()).hexdigest()`, and add `import hashlib` at the top with the other standard-library imports (alphabetical order: `asyncio`, `hashlib`, `uuid`). Leave `ticket_key` and `pipeline_version` as they are.

Change nothing else in the file and no other file.

## Finish

Report: done or not done, and the file changed. Never say a test passes; you have not run it.
