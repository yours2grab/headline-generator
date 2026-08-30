# Headline Generator, Product Log

A running record of every decision and change. Updated after any session where the skill is
modified.

---

## Purpose

Paste a draft, get nineteen headline and subheadline pairs, one in every shape, ordered by
the median engagement each shape earned in a real archive.

No ranking step, no "here are my three favourites". The nineteen come out strongest first
and the reader goes down the list until one lands.

## Who it is for

Anybody who publishes and stalls on the title. Works on any prose: an article, a post, an
email, a landing page.

## The problem it solves

Naming the thing is the last job and the one people do worst, usually at the end of a long
session when there is nothing left. Most people produce three titles, all in the same shape,
and pick the least bad one. Nineteen shapes forces range.

---

## Session Log

### 2026-08-28, v1.0 built overnight

- Built from the `hook` skill. 19 shapes mined from a 247 title public archive
- **Bug found and fixed:** `hook.py` had dead code reading `CFG["paths"]["shapes"]`, a key
  that never existed in the config. It would have raised on first call. Nothing called it
- Ships `templates.json` (311 examples) and `templates-lite.json` (the generation digest)
- Corpus attribution: the archive does not record whose titles they are, so the README says
  so plainly and names nobody

### 2026-08-30, v1.1 shipped

- Installed to `~/.claude/skills/`, copied to the vault, pushed to `yours2grab/headline-generator`
- Member page live at virgilbrewster.com/headline-generator-skill
- Page copy settled after several passes: title stays "The Headline Generator", the promise
  lives in the subheadline

## Open

- [ ] Reorder `templates.json` once the user has twenty of their own posts to rank against
- [ ] The ranking reflects the source archive's audience, not the reader's. Stated in the README
