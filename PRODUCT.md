# Headline Generator, Product Log

A running record of every decision and change. Updated after any session where the skill is
modified.

---

## Purpose

Paste a draft, get headline and subheadline pairs that are real top-performing titles with
only the topic words swapped for the draft's own (v2.0, 2026-11-22). One per shape the draft
can carry, strongest shape first.

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

### 2026-11-22, v2.0 rebuilt: copy real titles, swap only the topic words

- **Why:** v1 headlines read like imitation. The model only *modelled* each shape, a figure
  quota pushed numbers (and made-up "99% of writers" claims) into half the titles, and the
  fixed run of nineteen forced filler for shapes the draft could not carry
- **New library:** 63 frames in 18 shapes, every one a real 2026 Write Build Scale title
  (162 posts, 1 Jan to 20 Nov 2026) with its topic words opened as `{slots}`. Shapes ordered
  by the median likes of their frames. Titles with a dash, the word "actually" or a made-up
  crowd claim ("Top 1%") left out
- **New checker:** `hook.py run` takes `{"source", "candidates"}` and fails a title that changes
  any word outside the braces (`same_words`), and any number not in the source, matched with
  its k, m, % or + (`numbers_from_text`). List sizes in the source count. Years are free
- **Dropped:** the figure quota, the batch profile, the fixed run size, the old 247-title
  archive (`corpus.json`, `templates-lite.json`, `references/`)
- **Added:** podcast rules (no guest name in the title, no "Episode #" or "[Workshop]"),
  `hook.py frames` self-test
- **Kept:** the render page, unchanged
- Tested on real show notes: 4 bad titles caught (changed words, invented $12k, 30 days, 99%),
  4 good ones passed; then used to title 14 podcast episodes, 41 of 41 passed

## Open

- [ ] Reorder `templates.json` once the user has twenty of their own posts to rank against
- [ ] The ranking reflects the source archive's audience, not the reader's. Stated in the README
