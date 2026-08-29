#!/usr/bin/env python3
"""hook - the silent mechanics gate for two-deck headlines.

    score    read candidates as JSON on stdin, print a per check verdict
    batch    read ALL ten, compare the set against the archive's measured rates.
             exits 1 if the run does not look like the corpus.
    run      score + batch in ONE call. Prints only what failed, with the
             named fault. Exits 1 if anything failed. The fast path.
    render   read the final candidates on stdin, write the fixed
             white-ground HTML page to the path given as the next arg
             (or stdout). The model never hand-writes the page.

Four commands. This script reads. It writes nothing except the render,
and only to the path you hand it. There is no
ledger, no history, no state.

Every number and word list comes from config.json. There are no thresholds
in this file. If you need a new one, add it to the config.

The score this prints is for the model, not for the reader. See SKILL.md rule 1.
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
CHK = CFG["checks"]


# ---------------------------------------------------------------- helpers

WORD = re.compile(r"[A-Za-z'’]+")
TOKEN = re.compile(r"[A-Za-z'’]+|\d[\d,.]*")


def words(text):
    return WORD.findall(text or "")


def token_count(text):
    """Length counts digits too. '7 mistakes' is two words, not one."""
    return len(TOKEN.findall(text or ""))


def content_words(text, min_len):
    stop = set(CFG["stopwords"])
    return {w.lower() for w in words(text)
            if len(w) >= min_len and w.lower() not in stop}


def sentences(text):
    return [s for s in re.split(r"[.!?](?=\s|$)", text or "") if s.strip()]


def move_exempt(move, check_name):
    return move in CHK.get(check_name, {}).get("exempt_moves", [])


# ------------------------------------------------------------ the numbers

CLOCK = re.compile(r"\b\d{1,2}[:.]\d{2}\b|\b\d{1,2}\s?[ap]m\b", re.I)

NUM = re.compile(r"\$?\s?(\d[\d,]*(?:\.\d+)?)\s?([kKmM])?\b")
PLACEHOLDER = re.compile(r"\[[^\]]*\]")


def is_round(digits, suffix):
    """A round number reads as a claim. An odd one reads as a receipt.

    Trailing zeros alone are not the test, or $312,400 would read as round
    when it plainly reads as a figure somebody looked up. The test is how
    much survives once the trailing zeros come off: 300 leaves 3, and 340
    leaves 34.
    """
    bare = digits.replace(",", "")
    if suffix:
        return "." not in bare and CHK["figure_slot"]["round_if_bare_suffix"]
    if "." in bare:
        return False
    if not bare.endswith("0"):
        return False
    return len(bare.rstrip("0")) <= CHK["figure_slot"]["round_max_significant"]


def is_year(digits):
    lo, hi = CHK["figure_slot"].get("ignore_year_range", [0, -1])
    bare = digits.replace(",", "")
    return bare.isdigit() and lo <= int(bare) <= hi


def figures(text):
    """Returns (odd, round_, has_slot).

    Ratios are stripped first. '1:1' and '9 in 10' are ways of describing a
    shape, not figures anybody looked up, and counting them as receipts lets
    a headline pass the odd number rule without carrying any proof at all.
    """
    clean_text = text or ""
    for pat in CHK["figure_slot"].get("ignore_patterns", []):
        clean_text = re.sub(pat, " ", clean_text)
    odd, rnd = [], []
    for digits, suffix in NUM.findall(clean_text):
        if is_year(digits):
            continue
        (rnd if is_round(digits, suffix)
         else odd).append(digits + (suffix or ""))
    # A clock time is a figure. "4am" and "06:30" are the most concrete
    # numbers a headline can carry, and the pattern above misses them
    # because there is no word boundary between the digits and the "am".
    odd += [m.group(0) for m in CLOCK.finditer(clean_text)]
    return odd, rnd, bool(PLACEHOLDER.search(text or ""))


# ----------------------------------------------------------- the concrete

MONTHS = ("january february march april may june july august september "
          "october november december monday tuesday wednesday thursday "
          "friday saturday sunday").split()
COUNTED = ("one two three four five six seven eight nine ten eleven twelve "
           "twenty thirty forty fifty hundred thousand million dozen half "
           "first second third once twice").split()
WHEN = re.compile(r"\b(last|this|next)\s+(week|month|year|night|spring|"
                  r"summer|autumn|winter|thursday|friday)\b|"
                  r"\b(yesterday|tonight|this morning|that morning|"
                  r"the other day)\b", re.I)


def has_concrete(text):
    """A date, number, name, clock time, or a bracketed slot."""
    if re.search(r"\d", text or ""):
        return True
    if CLOCK.search(text or "") or WHEN.search(text or ""):
        return True
    low = (text or "").lower()
    if any(m in low for m in MONTHS):
        return True
    if set(w.lower() for w in words(text)) & set(COUNTED):
        return True
    if PLACEHOLDER.search(text or ""):
        return True
    # a capitalised word that is not the first word of ITS OWN sentence,
    # which is the cheapest available stand in for a proper noun
    for sent in sentences(text):
        if any(t[0].isupper() for t in words(sent)[1:]):
            return True
    return False


NEG_RUN = re.compile(r"\bno\b[^.,;]{0,30}[,;]\s*no\b", re.I)


def has_specific(text):
    """Beat one must be countable, dated, named, physical, or a strip list."""
    first = sentences(text)
    head = first[0] if first else (text or "")
    return has_concrete(head) or bool(NEG_RUN.search(text or ""))


# ---------------------------------------------------------------- the ban


def dirty(parts):
    hits = []
    blob = " ".join(p for p in parts if p)
    low = blob.lower()
    # An unfilled number slot is banned content, not a weak score. It rides
    # through every other check looking like a figure and lands on the page
    # as a promise with nothing behind it.
    n = CHK["figure_slot"]
    if n.get("bracket_only_fails") and re.search(n["empty_slot_pattern"], blob):
        hits.append("empty number slot")
    for w in CFG["banned_words"]:
        if re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", low):
            hits.append(w)
    for name, pat in CFG["banned_patterns"].items():
        if re.search(pat, blob):
            hits.append(name)
    return hits


# --------------------------------------------------------------- checking


def score(cand):
    title = cand.get("title", "")
    sub = cand.get("subhead", "")
    res = []

    # --- TITLE rules. 54% of the best titles name a result, 28% of the worst.
    n = CHK["names_a_result"]
    low_t = (title or "").lower()
    sig = [w for w in n["signals"] if w in low_t] or (["digit"] if re.search(r"\d", title or "") else [])
    res.append(("names_a_result", bool(sig), ", ".join(sig) if sig else "NAMES NO OUTCOME"))

    # A receipt beats a claim, and an empty bracket is neither. Her best
    # titles carry $247,347, not [$N]. Counting a slot as a figure is how ten
    # bracketed headlines scored a clean run and still said nothing.
    odd, rnd, slot = figures(title)
    if odd:
        res.append(("title_figure", True, "receipt: " + ", ".join(odd)))
    elif rnd:
        res.append(("title_figure", True, "round, reads as a claim: " + ", ".join(rnd)))
    else:
        res.append(("title_figure", False,
                    "EMPTY BRACKET, no figure" if slot else "no number"))

    res.append(("title_bracket", bool(re.search(r"\([^)]{3,}\)\s*$", title or "")),
                "bracket closer" if re.search(r"\([^)]{3,}\)\s*$", title or "") else "none"))

    res.append(("first_person", bool({"i","my","me"} & {w.lower() for w in words(title)}),
                "first person" if {"i","my","me"} & {w.lower() for w in words(title)} else "third person"))

    # 1 no continuation. 16% of the best, 33% of the worst.
    n = CHK["no_continuation"]
    lead = (sub or "").strip().lower()
    cont = any(lead.startswith(t) if t == "(" else
               re.match(r"^" + re.escape(t) + r"\b", lead)
               for t in n["reject_leading"])
    res.append(("no_continuation", not cont,
                "continues the title" if cont else "stands alone"))

    # 2 length. 15+ words in 40% of the best, 9% of the worst.
    n = CHK["subhead_length"]
    wc = token_count(sub)
    ok = n["min_words"] <= wc <= n["max_words"]
    note = "" if wc >= n["target_min"] else f", under the {n['target_min']} target"
    res.append(("subhead_length", ok,
                f"{wc} words, want {n['min_words']} to {n['max_words']}{note}"))

    # 3 two sentences. 19% of the best, 9% of the worst.
    n = CHK["two_sentences"]
    sc = len(sentences(sub))
    res.append(("two_sentences", sc >= n["min_sentences"],
                f"{sc} sentence(s)"))

    # 4 tension word. 19% of the best, 9% of the worst.
    n = CHK["tension_word"]
    low = (sub or "").lower()
    found = [w for w in n["words"] if re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", low)]
    res.append(("tension_word", bool(found),
                ", ".join(found) if found else "none"))

    # 5 no duplicated claim. Sharing words is fine, restating is not.
    n = CHK["no_duplicate_claim"]
    tw = content_words(title, n["min_word_length"])
    sw = content_words(sub, n["min_word_length"])
    shared = tw & sw
    ratio = (len(shared) / len(tw)) if tw else 0.0
    res.append(("no_duplicate_claim", ratio < n["max_shared_ratio"],
                f"reuses {len(shared)}/{len(tw)} of the title's words ({ratio:.0%})"
                + (": " + ", ".join(sorted(shared)) if shared else "")))

    # 6 clean
    hits = dirty([title, sub])
    res.append(("clean", not hits, ", ".join(hits) if hits else "clean"))

    total = sum(1 for _, ok, _ in res if ok)
    hard = [nme for nme, ok, _ in res
            if not ok and nme in CFG["scoring"]["hard_fail_checks"]]
    show = total >= CFG["scoring"]["min_points_to_show"] and not hard
    return res, total, hard, show


def cmd_score():
    raw = sys.stdin.read().strip()
    if not raw:
        sys.exit("no candidate on stdin")
    data = json.loads(raw)
    cands = data if isinstance(data, list) else [data]
    worst = 0
    for i, cand in enumerate(cands, 1):
        res, total, hard, show = score(cand)
        print(f"--- {i}. {cand.get('shape') or cand.get('title', '')[:48]}")
        for name, ok, detail in res:
            print(f"  {'PASS' if ok else 'FAIL'}  {name:<20} {detail}")
        print(f"  SCORE {total}/{CFG['scoring']['max_points']}"
              + (f"  HARD FAIL: {', '.join(hard)}" if hard else ""))
        print(f"  VERDICT {'SHOW' if show else 'REWRITE'}")
        if not show:
            worst = 1
    sys.exit(worst)


# ------------------------------------------------------- the batch check
#
# The failure this exists to stop: ten candidates that each pass their own
# rules while the SET looks nothing like the corpus. Checking one at a time
# cannot see that. This compares the whole run against her measured rates.

BAT = CFG["batch"]
PROFILE = {k: tuple(v) for k, v in BAT["profile"].items()}



def shared_figures(cands):
    """Rule 3b. No two candidates may lean on the same number.

    Nineteen shapes built on a draft's three strongest receipts is three hooks
    wearing nineteen costumes, and it reads that way on the page. The crowd claim
    is exempt: it is a statement about other people, so the same percentage
    appearing twice is a different fault and a rarer one.
    """
    seen = {}
    for c in cands:
        title = c.get("title", "")
        for raw in re.findall(r"\$?\d[\d,]*%?", title):
            key = raw.lstrip("$").rstrip("%").replace(",", "")
            if raw.endswith("%"):
                continue
            seen.setdefault(key, []).append(title[:44])
    return {k: v for k, v in seen.items() if len(v) > 1}


def cmd_batch():
    data = json.loads(sys.stdin.read())
    cands = data if isinstance(data, list) else [data]
    n = len(cands)
    if not n:
        sys.exit("no candidates")
    if n < BAT["min_candidates"]:
        sys.exit(f"batch needs the whole run, got {n}. Rates on a small set "
                 f"are meaningless. Score individually, then batch all ten.")
    rates, fails = {}, []
    for cand in cands:
        for name, ok, _ in score(cand)[0]:
            if name in PROFILE:
                rates[name] = rates.get(name, 0) + (1 if ok else 0)
    margin = BAT["ceiling_margin"]
    print(f"batch of {n}, against her best 57 (worst 57 sets the floor)")
    print(f"  {'feature':<18}{'yours':>7}{'hers':>7}{'floor':>7}{'ceil':>7}")
    for name, (hi, lo) in PROFILE.items():
        mine = round(100 * rates.get(name, 0) / n)
        floor, ceil = lo, min(100, hi + margin)
        bad = mine < floor or mine > ceil
        if mine < floor:
            fails.append(f"{name} {mine}% is under the {floor}% floor")
        elif mine > ceil:
            fails.append(f"{name} {mine}% is over the {ceil}% ceiling, "
                         f"the set does one thing every time")
        print(f"  {name:<18}{mine:>6}%{hi:>6}%{floor:>6}%{ceil:>6}%"
              f"  {'FAIL' if bad else 'ok'}")
    # Surface variety. Ten different templates still read as one headline
    # repeated when three of them open "Why I". Template variety is invisible
    # to the reader; the first two words are the first thing they see.
    k = BAT["opening_words"]
    seen = {}
    for cand in cands:
        key = " ".join(w.lower() for w in words(cand.get("title", ""))[:k])
        seen.setdefault(key, []).append(cand.get("title", "")[:44])
    stacked = {o: t for o, t in seen.items()
               if len(t) > BAT["max_titles_per_opening"] and o}
    print(f"\n  {'openings':<18}{len(seen):>6} distinct of {n}"
          f"  {'FAIL' if stacked else 'ok'}")
    for o, titles in stacked.items():
        fails.append(f'{len(titles)} titles open "{o}"')
        for t in titles:
            print(f"      {t}")

    dupes = shared_figures(cands)
    print(f"\n  {'figures':<18}{len(dupes):>6} reused"
          f"  {'FAIL' if dupes else 'ok'}")
    for fig, titles in dupes.items():
        fails.append(f'{len(titles)} titles lean on "{fig}"')
        for t in titles:
            print(f"      {t}")

    if fails:
        print("\nBATCH REJECTED. The set does not look like the corpus:")
        for f in fails:
            print("  " + f)
        print("Rewrite candidates until the rates clear the floor. Do not show "
              "this run.")
        sys.exit(1)
    print("\nBATCH OK")
    sys.exit(0)


# ------------------------------------------------- the one-call fast path
#
# Same score(), same batch math, same thresholds as the two commands above.
# The only difference is the plumbing: one invocation, and only the
# failures reach the transcript. A candidate that fails `score` fails here.


def batch_fails(cands):
    """The batch check as a list of fault strings. Same math as cmd_batch."""
    n = len(cands)
    rates, fails = {}, []
    for cand in cands:
        for name, ok, _ in score(cand)[0]:
            if name in PROFILE:
                rates[name] = rates.get(name, 0) + (1 if ok else 0)
    margin = BAT["ceiling_margin"]
    for name, (hi, lo) in PROFILE.items():
        mine = round(100 * rates.get(name, 0) / n)
        floor, ceil = lo, min(100, hi + margin)
        if mine < floor:
            fails.append(f"{name} {mine}% is under the {floor}% floor")
        elif mine > ceil:
            fails.append(f"{name} {mine}% is over the {ceil}% ceiling, "
                         f"the set does one thing every time")
    k = BAT["opening_words"]
    seen = {}
    for cand in cands:
        key = " ".join(w.lower() for w in words(cand.get("title", ""))[:k])
        seen.setdefault(key, []).append(cand.get("title", "")[:44])
    for o, titles in seen.items():
        if len(titles) > BAT["max_titles_per_opening"] and o:
            fails.append(f'{len(titles)} titles open "{o}": '
                         + " | ".join(titles))
    for fig, titles in shared_figures(cands).items():
        fails.append(f'{len(titles)} titles lean on "{fig}": '
                     + " | ".join(titles))
    return fails


def cmd_run():
    data = json.loads(sys.stdin.read())
    cands = data if isinstance(data, list) else [data]
    want = CFG["output"]["candidates_per_run"]
    bad = 0
    if len(cands) != want:
        print(f"run needs the whole set: got {len(cands)}, want {want}")
        bad = 1
    for i, cand in enumerate(cands, 1):
        res, total, hard, show = score(cand)
        if show:
            continue
        bad = 1
        print(f"--- {i}. {cand.get('shape') or cand.get('title', '')[:48]}"
              f"  REWRITE")
        for name, ok, detail in res:
            if not ok:
                print(f"  FAIL  {name:<20} {detail}")
        print(f"  SCORE {total}/{CFG['scoring']['max_points']}"
              + (f"  HARD FAIL: {', '.join(hard)}" if hard else ""))
    bfails = batch_fails(cands)
    if bfails:
        bad = 1
        print("BATCH: the set does not look like the corpus:")
        for f in bfails:
            print("  " + f)
    if bad:
        print("Rewrite the named candidates in their own shapes, run again. "
              "Do not show this run.")
        sys.exit(1)
    print(f"RUN OK  {len(cands)} candidates pass, batch clears. Render.")
    sys.exit(0)


# ----------------------------------------------------------------- render
#
# The page layout from SKILL.md Step 3, frozen: white ground, dark serif
# headline, muted subheadline, hairline rule between entries, each entry
# numbered under its shape name. Content in, page out. Nothing else.

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
    data = json.loads(sys.stdin.read())
    cands = data if isinstance(data, list) else [data]
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
    if cmd == "score":
        cmd_score()
    if cmd == "batch":
        cmd_batch()
    if cmd == "run":
        cmd_run()
    if cmd == "render":
        cmd_render()
    sys.exit(__doc__)
