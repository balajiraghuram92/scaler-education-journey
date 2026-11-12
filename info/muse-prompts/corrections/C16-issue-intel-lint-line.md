# C16 — `issue-intel/`: one long line

C14 worked. Reviewer's runs on the repository's code, no probe patches: **75 passed** with a database; every quickstart step exits 0; the sample repo's 12 C# tests pass; G1, G2 and the G4 report are written; G3 ends `offered=10/10 flipped=10` with all 10 backports `OPEN hidden=True`. mypy: the same three notes in `app/mcp_server/server.py` as before, not part of this prompt.

One lint error, from the SQL the reviewer's own C14 prompt supplied.

Logs: `info/muse-prompts/corrections/round18/`.

Paste everything below this line into Muse Code at the repository root.

---

Work only in `issue-intel/`. One agent. Do not run commands. Do not commit. Append what you did to `issue-intel/PROGRESS.md` under "C16".

## The one task — `app/search/hybrid.py:31`

```
app/search/hybrid.py:31:101: E501 Line too long (111 > 100)
```

The line is one of the two string pieces holding `replace(plainto_tsquery('english', :q)::text, '&', '|')::tsquery` inside `_fulltext`. Split that string literal across two adjacent literals so no line is longer than 100 characters. The SQL text sent to the database must be character-for-character the same as now, including spaces. Check the second occurrence in the same function and split it the same way if it is over the limit.

Change nothing else.

## Finish

Report: done or not done, and the file changed. Never say a check passes; you have not run it.
