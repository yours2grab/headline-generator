#!/usr/bin/env python3
"""hook - the silent gate for headlines built on Write Build Scale frames.

Rebuilt 2026-11-22. A headline passes only if it IS one of their real 2026
titles with nothing changed except the words inside the {slots}.

    run      read {"source": "...", "candidates": [...]} on stdin.
             Prints only what failed, with the named fault. Exits 1 if
             anything failed.
    score    same checks for one or more headlines he pasted, no source
             needed (the number check is skipped). Prints every check.
    frames   self-test: every frame must match its own source title.
    render   read the final candidates on stdin, write the fixed
             white-ground HTML page to the path given as the next arg
             (or stdout). The model never hand-writes the page.

This script reads. It writes nothing except the render, and only to the
path you hand it, never into the vault. Every word list and limit lives in
config.json.
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return json.load(fh)


CFG = load("config.json")
LIB = load(CFG["paths"]["templates"])


# ---------------------------------------------------------------- helpers

def norm(text):
    """Same text, minus the differences that are not words: curly quotes,
    double spaces, a trailing full stop or ellipsis."""
    t = (text or "").replace("’", "'").replace("‘", "'")
    t = t.replace("“", '"').replace("”", '"').replace("…", "")
    t = re.sub(r"\s+", " ", t).strip()
    return t.rstrip(". ")


SLOT = re.compile(r"\{[^}]*\}")


def frame_regex(frame):
    """Every word outside the braces must stay exactly as it is (case is
    ignored). Every {slot} takes at least one word from the source."""
    parts = SLOT.split(norm(frame))
    body = r"(.+?)".join(re.escape(p) for p in parts)
    body = body.replace(r"\ ", r"\s+")
    return re.compile(r"^" + body + r"$", re.I)


def find_frame(shape_name, frame_ref):
    for s in LIB["shapes"]:
        if s["shape"].lower() != (shape_name or "").lower():
            continue
        for f in s["frames"]:
            if norm(frame_ref).lower() in (norm(f["frame"]).lower(),
                                            norm(f["title"]).lower()):
                return s, f
        return s, None
    return None, None


NUM = re.compile(r"\d[\d,.]*\d[kKmM%+]?|\d[kKmM%+]?")


def numbers(text):
    """Every figure, with its k, m, % or + kept, so '$12k' never passes on
    the strength of a '12-day' somewhere in the text."""
    lo, hi = CFG["numbers"]["year_range"]
    out = []
    for m in NUM.findall(text or ""):
        bare = m.replace(",", "").rstrip(".").lower()
        if bare.isdigit() and lo <= int(bare) <= hi and len(bare) == 4:
            continue
        out.append(bare)
    return out


LIST_ITEM = re.compile(r"^\s*(?:[-*\u2022]|\d+[.)])\s+\S", re.M)


def numbers_in(source):
    """The figures the text states, plus the size of each list in it:
    three bullets under 'What we cover' is a real 3."""
    have = set(numbers(source))
    for block in re.split(r"\n\s*\n", source or ""):
        k = len(LIST_ITEM.findall(block))
        if k:
            have.add(str(k))
    return have


def sentences(text):
    return [s for s in re.split(r"[.!?](?=\s|$)", text or "") if s.strip()]


def dirty(parts):
    blob = " ".join(p for p in parts if p)
    low = blob.lower()
    hits = []
    if re.search(r"\{[^}]*\}|\[[^\]]*(?<![A-Za-z])[Nn](?![A-Za-z])[^\]]*\]", blob):
        hits.append("empty slot")
    for w in CFG["banned_words"]:
        if re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", low):
            hits.append(w)
    for name, pat in CFG["banned_patterns"].items():
        if re.search(pat, blob, re.I):
            hits.append(name)
    return hits


# --------------------------------------------------------------- checking

def check(cand, source=None):
    """Returns a list of (check, ok, detail)."""
    res = []
    title, sub = cand.get("title", ""), cand.get("subhead", "")
    shape, frame = find_frame(cand.get("shape"), cand.get("frame", ""))
    if not shape:
        res.append(("shape", False, f"no shape called {cand.get('shape')!r}"))
        return res
    if not frame:
        res.append(("frame", False,
                    "frame is not one of this shape's frames: "
                    + " | ".join(f["frame"] for f in shape["frames"])))
        return res
    m = frame_regex(frame["frame"]).match(norm(title))
    res.append(("same_words", bool(m),
                "keeps every fixed word of: " + frame["title"] if m else
                "CHANGES THEIR WORDS. Keep everything outside the braces of: "
                + frame["frame"]))
    if source is not None:
        have = numbers_in(source)
        filled = " ".join(m.groups()) if m else title
        made_up = [n for n in numbers(filled) + numbers(sub) if n not in have]
        res.append(("numbers_from_text", not made_up,
                    "NOT IN THE TEXT: " + ", ".join(made_up) if made_up
                    else "every number is in the text"))
    s = CFG["subhead"]
    sc, wc = len(sentences(sub)), len(re.findall(r"[A-Za-z'\d][\w'$%,./-]*", sub))
    res.append(("one_sentence", sc == s["sentences"],
                f"{sc} sentence(s), want {s['sentences']}"))
    res.append(("subhead_length", s["min_words"] <= wc <= s["max_words"],
                f"{wc} words, want {s['min_words']} to {s['max_words']}"))
    hits = dirty([title, sub])
    res.append(("clean", not hits, ", ".join(hits) if hits else "clean"))
    return res


def read_run():
    raw = sys.stdin.read().strip()
    if not raw:
        sys.exit("nothing on stdin")
    data = json.loads(raw)
    if isinstance(data, dict):
        return data.get("source"), data.get("candidates", [])
    return None, data


def cmd_run():
    source, cands = read_run()
    if not source:
        sys.exit('run needs {"source": "<the text he pasted>", "candidates": [...]}')
    bad = 0
    seen = {}
    for c in cands:
        seen.setdefault((c.get("shape") or "").lower(), 0)
        seen[(c.get("shape") or "").lower()] += 1
    for k, v in seen.items():
        if v > CFG["output"]["max_per_shape"]:
            print(f"{v} entries in shape {k!r}, max {CFG['output']['max_per_shape']}")
            bad = 1
    for i, cand in enumerate(cands, 1):
        fails = [r for r in check(cand, source) if not r[1]]
        if not fails:
            continue
        bad = 1
        print(f"--- {i}. {cand.get('shape')}: {cand.get('title', '')[:60]}  REWRITE")
        for name, _, detail in fails:
            print(f"  FAIL  {name:<18} {detail}")
    if bad:
        print("Rewrite the named entries on the same frame, or drop a shape the "
              "text cannot carry. Do not show this run.")
        sys.exit(1)
    print(f"RUN OK  {len(cands)} entries pass. Render.")
    sys.exit(0)


def cmd_score():
    source, cands = read_run()
    worst = 0
    for i, cand in enumerate(cands if isinstance(cands, list) else [cands], 1):
        print(f"--- {i}. {cand.get('shape')}: {cand.get('title', '')[:60]}")
        for name, ok, detail in check(cand, source):
            print(f"  {'PASS' if ok else 'FAIL'}  {name:<18} {detail}")
            worst = worst or (0 if ok else 1)
    sys.exit(worst)


def cmd_frames():
    bad = 0
    n = 0
    for s in LIB["shapes"]:
        for f in s["frames"]:
            n += 1
            if not frame_regex(f["frame"]).match(norm(f["title"])):
                print(f"FRAME DOES NOT MATCH ITS OWN TITLE: {s['shape']}: {f['frame']}  vs  {f['title']}")
                bad = 1
            fixed = SLOT.sub(" ", f["frame"])
            hits = [h for h in dirty([fixed]) if h != "empty slot"]
            if hits:
                print(f"FRAME KEEPS A BANNED WORD ({', '.join(hits)}): {f['frame']}")
                bad = 1
    print(f"{n} frames in {len(LIB['shapes'])} shapes: {'FAIL' if bad else 'all match their own titles'}")
    sys.exit(bad)


# ----------------------------------------------------------------- render
#
# The page layout, frozen: white ground, dark serif headline, muted
# subheadline, hairline rule between entries, each entry numbered under
# its shape name. Content in, page out. Nothing else.

PAGE_TOP = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hooks</title>
<style>
  body { background: #ffffff; color: #1a1a1a;
         font-family: Georgia, 'Times New Roman', serif;
         max-width: 660px; margin: 0 auto; padding: 56px 24px 96px; }
  .entry { padding: 28px 0; border-bottom: 1px solid #e5e5e5; }
  .entry:last-child { border-bottom: none; }
  .shape { font-family: Helvetica, Arial, sans-serif; font-size: 11px;
           letter-spacing: .14em; color: #999999; margin: 0 0 10px; }
  h2 { font-size: 22px; line-height: 1.3; font-weight: 600; margin: 0 0 8px; }
  .sub { font-size: 16px; line-height: 1.5; color: #666666; margin: 0; }
</style>
</head>
<body>
"""

PAGE_BOTTOM = "</body>\n</html>\n"


def cmd_render():
    import html as html_mod
    source, cands = read_run()
    entries = []
    for i, cand in enumerate(cands, 1):
        shape = html_mod.escape(cand.get("shape", ""))
        title = html_mod.escape(cand.get("title", ""))
        sub = html_mod.escape(cand.get("subhead", ""))
        entries.append(
            f'<div class="entry">\n'
            f'  <p class="shape">{i}. {shape}</p>\n'
            f'  <h2>{title}</h2>\n'
            f'  <p class="sub">{sub}</p>\n'
            f'</div>\n')
    page = PAGE_TOP + "".join(entries) + PAGE_BOTTOM
    out = sys.argv[2] if len(sys.argv) > 2 else None
    if out:
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(page)
        print(f"rendered {len(cands)} entries to {out}")
    else:
        sys.stdout.write(page)
    sys.exit(0)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    {"run": cmd_run, "score": cmd_score, "frames": cmd_frames,
     "render": cmd_render}.get(cmd, lambda: sys.exit(__doc__))()
