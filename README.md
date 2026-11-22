# Headline Generator

Paste a draft. Get headline and subheadline pairs that read exactly like a top Substack
publication, because each one **is** one of their real titles with only the topic words swapped
for yours.

Works on an article, a newsletter issue, an email, a podcast episode or a live.

## Install

```bash
git clone https://github.com/yours2grab/headline-generator.git ~/.claude/skills/headline-generator
```

Then in Claude Code: `hook`, `headlines`, `subject line`, `title this episode` or
`what should I call this`.

## What it needs

Nothing. No API key, no account, no network. The checker is plain Python 3 and runs offline.

## What it writes

One HTML file, to a temp path you give it. That is the only file this skill creates.
No ledger, no history, no state.

## How it works (v2.0)

`data/templates.json` holds **63 frames in 18 shapes**. Every frame is a real 2026 title from
Write • Build • Scale, one of the biggest publications about growing on Substack, with only its
topic words opened as `{slots}`:

```
How I'd Fix Any Substack in 30 Minutes      (888 likes, their best post of 2026)
How I'd {verb} Any {thing} in {time}
```

The skill keeps every word outside the braces and fills the braces from your draft:

```
How I'd Fix Any Sales Page in 30 Minutes
```

The 18 shapes, strongest first (median likes of their frames):

NEWS HOOK · THE RULE · STOP + PAYOFF · HOW I'D · WHY MOST · NUMBER LIST · NOBODY TOLD ME ·
THE 1 X · I ANALYZED N · I'VE WORKED WITH N · BIG-NUMBER LIST · THE X THAT ·
WHY + COLON + NUMBER · HOW TO (WITHOUT X) · ONE WORD IN CAPS · HOW WE DID IT · GUEST STORY ·
GUEST'S BELIEF

## The checker

`scripts/hook.py run` rejects a headline when:

- **It changes their words.** One added, dropped or swapped word outside the braces fails.
- **It has a number that is not in your draft.** `$12k` needs `$12k` in the text, with the k.
  The size of a list in your draft counts: three bullets is a real 3. Years are free.
- **The subheadline is more than one sentence, or outside 3 to 16 words.**
- **It uses a banned word or pattern:** dashes, "Episode #", "[Workshop]", and anything you add.

```bash
python3 scripts/hook.py frames                    # self-test: every frame matches its real title
python3 scripts/hook.py run    < run.json         # {"source": "...", "candidates": [...]}
python3 scripts/hook.py render out.html < run.json
```

## Rules worth knowing

- **Only the shapes your draft can carry.** No fixed count. Five real headlines beat eighteen
  with filler.
- **No invented numbers, no invented crowd claims.** "99% of writers" only appears if your
  draft says it.
- **Podcasts and lives:** the guest's name never goes in the title. Use "How This Creator…",
  "She Spent Years…" or the guest's own line, and put the name in the subheadline.

## Make it yours

`config.json` holds every limit and word list. `banned_words` ships with one word family: add
your own AI tells. To add a frame, copy a real title into `data/templates.json`, open its topic
words as `{slots}`, and run `python3 scripts/hook.py frames`.

## What changed from v1

v1 had 19 shapes from an anonymous 247-title archive and asked the model to *imitate* each
shape, with a figure quota and a fixed run of nineteen. The result read like imitation. v2 drops
the quota, the fixed count and the old archive, and copies real titles word for word.
See `PRODUCT.md` for the full log.
