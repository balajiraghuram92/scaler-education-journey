# Brief: recover script-held lesson text for the Neuralascent migration

We are moving lesson pages from a static site into a learning platform that stores each lesson
as Markdown. A converter already turned each page's HTML into Markdown. What it cannot see is
learner-facing text that lives **inside each page's inline `<script>`**: glossary definitions
shown in pop-ups, the text a step-through diagram shows for each step, tab panels, scenario
pickers, simulator explanations and similar. Some HTML widgets (chat mock-ups, etc.) were also
missed. Your job is to put that text into the lesson **verbatim**, as plain Markdown, next to
the content it belongs to.

## Paths (all absolute)

- Site root (original pages, read-only): `C:\Users\balaj\Documents\balajiraghuram.github.io`
- Tool folder: `C:\Users\balaj\AppData\Local\Temp\claude\C--Users-balaj-Documents-scaler-education-journey\71ef8431-9172-4ca6-ba7c-fbb548e18ca4\scratchpad\conv`
  - `out/<key>.json` — converter output: `{ sections: [{ title, md }], diagrams: [{ key, title, ... }], mcqs }`
  - `out/<key>.miss.txt` — every text run the checker could not find in the output (`[js]` = from a script, `[html]` = from markup)
  - `verify.mjs` — the checker
- Write your result to: `<tool folder>\supplements\<key>.json` (create the `supplements` folder if needed)

## How to work

1. Read `out/<key>.miss.txt`, then read the page's inline `<script>` blocks in the original HTML
   (search the file for `<script>`). Work out which UI each missing string belongs to: which
   diagram (match by element ids / `data-*` attributes / button labels to the surrounding HTML),
   which glossary term (the `data-k` attribute on `<button class="kw" data-k="...">` maps to keys in
   a glossary object), which tab, which simulator.
2. Find where it belongs in `out/<key>.json`: the section (by exact `title`) and an exact anchor
   line inside that section's `md` — usually a `{{diagram:<key>}}` token, a heading line such as
   `#### The parts of an agent`, or a full paragraph line. Anchors must be copied exactly,
   character for character, from the `md` string (one whole line, as split on `\n`).
3. Write the supplement JSON:

```json
{
  "page": "<relative page path>",
  "inserts": [
    {
      "section": "<exact section title from out/<key>.json>",
      "after": "<exact full line from that section's md, or \"\" to append at the end of the section>",
      "md": "<Markdown to insert>"
    }
  ],
  "glossary": [ { "term": "Large language model (LLM)", "definition": "A model trained on ..." } ],
  "skipped": [ { "text": "<string you deliberately left out>", "reason": "button label / CSS / duplicate of visible text / code identifier ..." } ]
}
```

   - `glossary`: every glossary entry in the page's script, in the order the script defines them.
     Use the display name the page shows for the term (the visible button text or the glossary
     entry's own title field) and the definition verbatim. Do not also put glossary entries in
     `inserts`.
4. Check yourself:
   `node verify.mjs "C:\Users\balaj\Documents\balajiraghuram.github.io" <page> out\<key>.json supplements\<key>.json`
   (run from the tool folder; add `VERBOSE=1` in front to list what is still missing — in
   PowerShell use `$env:VERBOSE='1'; node ...`). Iterate until every remaining miss is in your
   `skipped` list with a reason. Validate that your JSON parses (`node -e "JSON.parse(require('fs').readFileSync('supplements/<key>.json','utf8'))"`).

## Rules — these matter most

- **Verbatim.** Copy the words exactly as the script has them. Only convert markup: HTML tags
  to Markdown (`<b>`/`<strong>` → `**x**`, `<em>` → `*x*`, `<code>` → `` `x` ``, `<br>` → new line,
  lists → `- `), JS escapes (`\'`, `\n`, `\u2019`) to the real characters, and template pieces
  like `${x}` to the value they show if obvious, else drop them. Never paraphrase, summarise,
  shorten, correct or add your own sentences. The only words you may write yourself are short
  labels that name what a block is, e.g. `**Step 3 · Call servers:**` or `**If you pick "Claude Haiku 4.5":**`,
  taken from the button/tab labels in the page.
- Markdown subset only: paragraphs, `- ` / `1. ` lists (no nesting), pipe tables, `> **Label:**`
  callouts (every callout line starts with `> `), `#### ` and `##### ` headings, fenced code.
  No raw HTML.
- Interactive widgets become static text in the order the UI walks through them, e.g. a
  step-through diagram becomes a list with one item per step: `- **1. Request:** <panel text>`.
- Do not include text that is already present in the output (the checker tells you what is missing).
- Do not edit `out/*.json`, the original site, or any file other than your supplement.
- Never create Python files.
- Finish by replying with: the supplement path, the final checker line, and counts of inserts,
  glossary entries and skipped strings.
