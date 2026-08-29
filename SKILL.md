---
name: headline-generator
description: Writes headlines and subheadlines for anything you publish: an article, a blog post, a newsletter issue, an email, a landing page. Paste the text, get nineteen pairs, one in every shape, from a library of 19 title templates mined from a 247-title published archive. Triggers on: hook, hooks, headline, headlines, title, subhead, subheadline, subject line, give me hooks, headline options, name this post, what should I call this.
allowed-tools: Read Grep Glob Bash
---

# Headline Generator

Paste text, get nineteen headline and subheadline pairs, one in every shape. That is the whole tool.

---

## HARD RULES

1. **Always nineteen. One per shape. Never fewer.** Every shape in `data/templates.json` gets exactly one candidate, every run. No shape is skipped, no shape appears twice. If a candidate fails in Step 2, rewrite it **in that same shape** until it stands — nothing is ever dropped, because dropping one means a shape goes missing. Never hand back a short run and never explain a shortfall on the page.
2. **Label every candidate with its shape.** The point is to see the range, not guess at it. The shape name from `templates.json` goes on the page above each pair. Scores, job tags, drop notes and closing questions still never reach the page.
2b. **There is no selection step. Walk the file.** `templates.json` holds the 19 shapes already ordered by median engagement, STOPPED DOING at 96 down to PERSONAL CONFESSION at 35. Go top to bottom, write one candidate in each, keep that order on the page. Entry 1 is always the archive's strongest shape and entry 19 always the archive's weakest, every run, so the reader can read down until one lands. Never rank, never reorder, never drop the weak ones: QUESTION and PERSONAL CONFESSION are on the page precisely because every shape earns its slot. Never force a shape by inventing material.
3. **Never show the score.** `hook.py` prints a verdict for you, not for the user.
3b. **One figure, one entry.** No two candidates in a run may lean on the same number. Nineteen shapes built on the draft's three strongest receipts is three hooks wearing nineteen costumes, and it reads that way on the page. Spread the figures the way the shapes are spread: if `312 subscribers` carries entry 15, entry 18 finds a different one. When a shape's natural figure is already spent, take the next real specific in the draft rather than reusing it, and if the draft has none left, write that shape without a number.
4. **Every figure comes from the source text.** Quote it exactly as the draft states it: `22 emails`, `9 pre-launch`, `email 1, 7, 25`. Never invent one and never ask the user to verify one. **A bracket is not a number.** `[N]` is a promise with nothing behind it and `hook.py` hard-fails it. If the draft has no figures, see Step 1a: the shape still gets written, around a real specific instead of a number. The one exception is the crowd claim, the archive's `99% of writers ignore`, which is always about other people and never about your results.
5. **Write nothing to disk.** No ledger, no history, no files. The one exception is the Step 3 render, which goes to a temp directory and nowhere else.
6. **Respect the ban list.** Every word in `config.banned_words` is a hard fail. The list ships nearly empty — add your own.
7. **Never invent a threshold.** Every rule number lives in `config.json`.
8. **Never invent a template, a pattern name, or a rule.** Everything comes from `data/templates-lite.json` (the generation digest), its source `data/templates.json`, `references/examples.md` and `references/formula.md`. If you find yourself naming a structure that is not in those files, stop: you are making it up. Every candidate must be modelled on a real example you actually read from the file.
9. **Never show a run that failed Step 2.**

---

## Step 0, load (silent)

1. `data/templates-lite.json` — **the whole load, one file.** The 19 shapes in run order with their forms and 2 strongest real examples each, the formula (verbatim copy of `references/formula.md`), and the check digest under `write_to_the_checks` (generated from `config.json`: every threshold, hard fail, batch floor and the ban list the scorer will hold you to).

**Everything else stays on the shelf:** the full `data/templates.json` (311 examples, all 247 titles), `references/examples.md` (the same, readable), `data/corpus.json`, `references/formula.md` (source of the embedded copy) and `config.json` (the authority on every threshold — the digest is generated from it). Open a shelf file only when a shape's two examples in the lite file are not enough to model a candidate. If the lite file ever disagrees with a source file, the source wins and the lite file gets regenerated.

**These files are the only authority.** If a structure is not in the template files, you are making it up. Read the real examples before writing.

---

## Step 1, generate

**The source arrives with the request.** The user pastes the article, draft, transcript or email. Read it and write. Never go looking for material: no archive, no past drafts, no searching. Ask only if nothing was sent.

### 1a. Count the receipts FIRST, before you write a single title

Read the source for real figures: revenue, subscriber counts, time to a result, a dated before and after. **What you find decides how the four receipt shapes get written, never whether they get written.** All 19 run every time.

**The text carries real figures** → the receipt shapes work as designed. MONEY RECEIPT, TIME BOUND, SUBSCRIBER RECEIPT, CLIENT / THIRD PARTY. Use the figure exactly as the source states it. Odd beats round: the archive's biggest post carries `$247,347`, not `$250K`. A figure alone is worth almost nothing (`MONEY RECEIPT` is +3 on the archive's median across 49 uses) — it pays when it is divided by a second number. `2hrs/day → $247,347`. `10 systems → 38.9K subs → in 4 months`. The hook is the ratio, not the sum.

**The text carries no figures** → the receipt shapes still get their slot, built on **a real specific instead of a number**: a named thing, a dated moment, a physical detail, something countable in the draft itself. This is not the consolation lane: **18 of the archive's top 50 carry no digit anywhere**, including the archive's 277, the archive's 262 and the archive's 140. Expect those four entries to be the weakest on the page, and let them be — every shape earns its slot, including the ones a given draft cannot fully feed.

**Never bracket your way across the gap.** `[N]` is not a number, it is a promise of one, and a run of them is nineteen headlines that say nothing. `hook.py` hard-fails any candidate containing an unfilled slot. Never invent a figure and never ask the user to fill one in. The only figure you may invent is the crowd claim — the archive's `99% of writers ignore` — because it is a statement about other people, never about your results.

**Plan the digits before drafting, not after.** Step 2 holds the run to the corpus profile (in the `write_to_the_checks` digest you loaded, sourced from `config.json`), and its `title_figure` floor means roughly half the titles need a filled figure. Count what the draft gives you, give each real figure its one entry (rule 3b), and when the draft cannot cover the floor on its own, write the sanctioned extras into the FIRST draft: crowd-claim percentages (each entry its own odd number, always about other people) and real counts of things the draft itself states. A first batch rejected for missing figures is a planning failure, not new information — one generate, one score pass, one batch pass is the whole run.

### 1b. Write one candidate per shape, in file order

Open `data/templates-lite.json` and go down the list: STOPPED DOING, TIME BOUND, NOBODY / UNTIL, THE X PLAYBOOK, HOW I DID IT, IGNORED BY MOST, THE RESET, PERCENT PROPHECY, WHY + CLAIM, SUBSCRIBER RECEIPT, BRACKET CLOSER, HOW TO, MONEY RECEIPT, DIRECT ADDRESS, CLIENT / THIRD PARTY, CONTRARIAN FLIP, NUMBERED LIST, QUESTION, PERSONAL CONFESSION. Nineteen shapes, nineteen candidates, that order on the page.

Read the shape's `forms` and its real `examples` before writing its candidate. Model it on an example you actually read. `BRACKET CLOSER` is flagged in the data as a modifier rather than a shape, so its entry is a complete claim with the parenthetical doing the work — it will read as the thinnest entry in the run and that is expected.

**Vary the opening words.** Shape variety is not surface variety. Nineteen different templates can still produce three titles that open "Why I" and read identically. `hook.py batch` rejects a run where two titles share their first two words, so nineteen entries means nineteen distinct openings.

The subheadline: **[SPECIFIC] + [CONSEQUENCE, UNRESOLVED]**. Beat one is countable, dated, named or physical. Beat two says what changes, never how. 15 words or more, two sentences, a tension word where it fits, and never continuing the title.

Repeat the title's nouns freely. Never repeat the claim.

---

## Step 2, check the run (silent, one call)

**All nineteen, score AND batch, in one invocation. Never check one at a time.**

```bash
python3 scripts/hook.py run <<'JSON'
[ {"shape":"STOPPED DOING","title":"...","subhead":"..."}, ...all nineteen... ]
JSON
```

Same ten checks per candidate and the same whole-set comparison against the archive's measured rates as before — `run` just does both at once and **prints only what failed, with the named fault**. Silence on a candidate means it passed. The batch half is the only check that catches invention: individual candidates can each pass their own rules while the set looks nothing like the corpus, which is exactly how a full run with zero numbers in it got shipped once.

On exit 1: rewrite the named candidates **in their own shapes** — never drop one, every shape owes the page an entry — and pipe all nineteen through `run` again. Because you wrote the first draft to the check digest in Step 0, one rewrite pass is the expected worst case. **Do not show a rejected run.** Do not explain the rejection. Fix it and show the fixed run.

(`score` and `batch` still exist as separate commands for checking a single headline the user pastes. The full run never uses them.)

---

## Step 3, present

**Never hand-write the HTML.** The page layout — white paper, dark serif headline, muted subheadline, hairline rule between entries, all nineteen numbered in `templates.json` order under their shape names — is frozen inside `hook.py`. Feed it the passing run and a temp path:

```bash
python3 scripts/hook.py render "${TMPDIR:-/tmp}/hooks.html" <<'JSON'
[ ...the nineteen that passed, in file order... ]
JSON
```

Then open it in the browser:

```bash
open "${TMPDIR:-/tmp}/hooks.html"
```

The HTML is a render, written to a temp path. It is the only file this skill creates.

Then stop.

---

## Check an existing headline

The user can paste one they wrote. Score it, then give the rewrite. Say what is wrong in plain craft language, never in points.

---

## What this does NOT do

- Write the article. That is a different skill.
- Write ad hooks. Different job, different shapes.
- Save, log or remember anything.
- Read anything outside its own folder.
