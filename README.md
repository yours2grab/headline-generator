# Headline Generator

Paste a draft. Get nineteen headline and subheadline pairs, one in every shape.

Works on anything you publish: an article, a blog post, a newsletter issue, an email, a
landing page, a video description.

There is no ranking step and no "here are my three favourites." The nineteen shapes are
already ordered by median engagement, strongest first. You read down until one lands.

## Install

```bash
git clone https://github.com/yours2grab/headline-generator.git ~/.claude/skills/headline-generator
```

Then in Claude Code: `hook`, `headlines`, `subject line`, or `what should I call this`.

## What it needs

Nothing. No API key, no account, no network. The scoring script is plain Python 3
and runs offline.

## What it writes

One HTML file, to a temp path you give it. That is the only file this skill creates.
No ledger, no history, no state.

## The nineteen shapes

STOPPED DOING · TIME BOUND · NOBODY / UNTIL · THE X PLAYBOOK · HOW I DID IT ·
IGNORED BY MOST · THE RESET · PERCENT PROPHECY · WHY + CLAIM · SUBSCRIBER RECEIPT ·
BRACKET CLOSER · HOW TO · MONEY RECEIPT · DIRECT ADDRESS · CLIENT / THIRD PARTY ·
CONTRARIAN FLIP · NUMBERED LIST · QUESTION · PERSONAL CONFESSION

## Where the shapes come from — read this before you trust the order

The nineteen shapes were mined from **one creator's public archive**: 247 published titles,
198 with subheadlines, median 43 likes. 174 of the 247 matched a shape, so coverage is 70%.
Every threshold in `config.json` — subheadline length, the figure floor, the batch ceilings —
was measured off that same archive, comparing its best 57 posts against its worst 57.

That means two things.

**The shapes are real.** They are not invented patterns. Every example in `data/templates.json`
is a title that was actually published, with the engagement it actually got.

**The ranking is one audience's, not yours.** STOPPED DOING sits at 96 and PERSONAL CONFESSION
at 35 because that is how *that* audience responded. Your readers may be different. Use the
order as a starting sequence, not a law. After twenty of your own posts, you will know which
shapes work for you, and you can reorder `data/templates.json` to match.

The archive owner is not named here because the source data does not record it.

## Two gates before anything reaches the page

`scripts/hook.py` runs ten checks per candidate and one whole-set check.

The per-candidate checks catch the usual failures: a subheadline that continues the title
instead of standing alone, a subheadline that restates the title's claim, an unfilled `[N]`
placeholder, a banned word.

The whole-set check is the one that matters. Nineteen candidates can each pass on their own
while the set looks nothing like a real archive — nineteen titles that all carry a number
and all name a result read as one headline written nineteen times. The batch check has both
a floor and a ceiling for exactly that reason, and it will reject a run that does one thing
every time.

```bash
python3 scripts/hook.py run    < candidates.json   # both gates, one call
python3 scripts/hook.py render out.html < candidates.json
```

## Rules worth knowing

- **Every figure comes from your draft.** The skill never invents a number and never asks you
  to fill one in. If your draft has no figures, the shape still gets written, built on a real
  specific instead — a named thing, a dated moment, something countable in the text.
- **One figure, one entry.** No two candidates lean on the same number. Nineteen shapes built
  on your three best receipts is three headlines wearing nineteen costumes.
- **All nineteen, every time.** A candidate that fails is rewritten in its own shape, never
  dropped. A short run means a shape went missing.

## Make it yours

`config.json` holds every threshold and word list. `SKILL.md` contains no magic numbers.

- `banned_words` ships with one entry. Add your own AI tells.
- `publication` and `author` are blank and optional. Neither affects generation.
- Every check threshold can be changed. If you change one, the skill obeys it.
