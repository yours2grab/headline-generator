---
name: headline-generator
description: Writes headlines and subheadlines for an article, newsletter issue, email, podcast episode or live. Every headline is a real Write Build Scale title from 2026 with only its topic words swapped for the text's own words, checked by a script that rejects any changed word and any number that is not in the text. One entry per shape the text can carry, from 18 shapes and 63 real frames. Every byline is one short sentence. Triggers on: hook, hooks, headline, headlines, title, subhead, subheadline, subject line, give me hooks, headline options, name this post, what should I call this, title this episode.
allowed-tools: Read Grep Glob Bash
---

# Headline Generator

Paste text, get headline and subheadline pairs that sound exactly like Write Build Scale, because each one IS one of their 2026 titles with only the topic words swapped. That is the whole tool.

v2.0, 2026-11-22: rebuilt so every headline copies a real title word for word instead of loosely imitating a shape.

---

## HARD RULES

1. **Copy the frame, swap only the braces.** Every shape in `data/templates.json` holds frames: a real Write Build Scale title with its topic words opened as `{slots}`. Keep every word outside the braces exactly as it is, in the same order. Fill each slot with words from the source text. `hook.py` rejects a title that adds, drops or changes one fixed word.
2. **Every number comes from the text.** A figure in a slot or a subhead must be written in the text, with its k, m, % or + (`$12k` needs `$12k` in the text, not a `12-day` somewhere). The size of a list in the text counts: three bullets is a real 3. Four-digit years are free. Never invent a number, never invent a crowd claim like "99% of writers", never ask the user to fill one in. A frame whose `{N}` the text cannot fill is a frame you skip.
3. **Only the shapes the text can carry.** One entry per shape at most, and only where a frame fits the text without forcing it. Five strong entries beat eighteen with filler. There is no fixed count and no number quota.
4. **Label every entry with its shape.** The shape name goes above each pair on the page. Scores, frame names and checker output never reach the page.
5. **Write nothing to disk** except the Step 3 render, which goes to a temp directory and nowhere else.
6. **Respect the ban list.** Every word in `config.banned_words` and every pattern in `config.banned_patterns` is a hard fail. Add your own.
7. **Never invent a frame, a shape or a rule.** Everything comes from `data/templates.json` and `config.json`. If no frame fits, skip the shape.
8. **Never show a run that failed Step 2.**

---

## Step 0, load (silent)

`data/templates.json`, the whole load. 18 shapes ordered by the median likes of their frames (NEWS HOOK at 147 down to GUEST'S BELIEF at 50.5), 63 frames, each with the real title, its subhead, likes, date and whether it was a podcast episode or an article.

---

## Step 1, generate

**The text arrives with the request.** The user pastes the article, draft, show notes, transcript or email. Read it and write. Never go looking for a story elsewhere. Ask only if nothing was sent.

1. **Go down the shapes in file order.** For each shape, read its frames and pick the one frame the text can fill most naturally. If none fits without forcing, skip the shape.
2. **Fill the slots from the text.** Use the text's own nouns, results and numbers. The slot hint (`{result}`, `{group}`, `{time}`) says what kind of words go in; the source title shows how long they run. Keep the fixed words' capitals the way the source title has them.
3. **The subheadline: one short sentence, 3 to 16 words.** Model it on the frame's real subhead: same length, same job. Never repeat the title's claim. Numbers in it follow rule 2.

### Podcast episodes and lives

How Write Build Scale titles their episodes in 2026:

1. **Never put the guest's name in the title.** No "(Guest Name)" at the end. Use the GUEST STORY frames ("How This Creator…", "She Spent Years…") or GUEST'S BELIEF (the guest's own line as the title). The subhead can say who the guest is.
2. **No "Episode #N", no "[Workshop]", no "[Livestream Replay]", no "Live with…".** `hook.py` rejects the first three.
3. **Digits always:** "3", "30 Days", never written out.

---

## Step 2, check the run (silent, one call)

```bash
python3 scripts/hook.py run <<'JSON'
{"source": "<the full text the user pasted>",
 "candidates": [
  {"shape": "THE 1 X", "frame": "<the frame or its real title>", "title": "...", "subhead": "..."},
  ...
 ]}
JSON
```

It prints only what failed: `same_words` (a fixed word changed), `numbers_from_text` (a number not in the text), `one_sentence`, `subhead_length`, `clean` (banned words, dashes, empty slots, episode tags). Silence on an entry means it passed.

On exit 1: rewrite the named entries **on the same frame**, or drop that shape if the text cannot carry it, and run again. Never show a rejected run and never explain the rejection to the user.

---

## Step 3, present

Never hand-write the HTML. The page layout is frozen inside `hook.py`. Feed it the passing run, in file order:

```bash
python3 scripts/hook.py render "$TMPDIR/hooks.html" <<'JSON'
{"candidates": [ ...the entries that passed... ]}
JSON
open "$TMPDIR/hooks.html"
```

The HTML is a render in a temp directory, never a file in the user's project. Then stop.

---

## Check an existing headline

The user can paste one they wrote. Run `python3 scripts/hook.py score` on it against the nearest frame, then give them the rewrite on that frame. Say what is wrong in plain words, never in check names.

---

## Maintenance

- `python3 scripts/hook.py frames` checks that every frame still matches its own real title and keeps no banned word. Run it after any change to `data/templates.json`.
- New frames come only from real Write Build Scale titles. Leave out any title whose fixed words break the ban list or carry a made-up crowd claim.

---

## What this does NOT do

- Write the article.
- Write ad hooks.
- Save, log or remember anything.
- Touch your files.
