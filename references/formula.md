# The formula

Built from 198 title and subheadline pairs pulled from a public archive, split into the 57 most-liked and the 57 least-liked. Every number below was computed from `data/corpus.json`, which sits in this folder. Read real rows from it before writing. Do not invent an example when a real one exists.

```
HEADLINE  = [ SHAPE ]
SUBHEAD   = [ SPECIFIC ] + [ CONSEQUENCE, UNRESOLVED ]
```

---

## What the data actually supports

| Pattern in the subheadline | Best 57 | Worst 57 | Gap | Verdict |
|---|---|---|---|---|
| 15 words or longer | 40% | 9% | +31 | **strongest** |
| Continues from the title | 16% | 33% | −17 | **strongest, inverted** |
| Shares no long word with title | 61% | 74% | −13 | **inverted, see below** |
| Two or more sentences | 19% | 9% | +10 | holds |
| Carries a tension word | 19% | 9% | +10 | holds |
| Both pronoun lanes in one line | 7% | 0% | +7 | weak |
| Switches pronoun lane | 51% | 46% | +5 | weak |
| Contains a digit | 33% | 30% | +3 | **dead** |
| Six words or fewer | 16% | 19% | −3 | **dead** |

Median subheadline length: **13 words** in the best, **9** in the worst.

### The four rules

**1. Write long. 15 words or more.** The single biggest gap in the data, 40% against 9%. Target 12 to 22. Under 12 reads as a caption.

**2. Never continue the title.** No opening bracket, no "and", "but", "or", "so", "then". The only pattern that appears twice as often in the worst posts as the best. Hard refuse.

**3. Two sentences beat one.** 19% against 9%. The full stop in the middle is where the reader decides to keep going.

**4. Carry a tension word.** nobody, never, without, wrong, most, stop, quit, fail. 19% against 9%.

### Three rules that died

Stated plainly because they were in this skill and they were wrong.

**Digits are not a signal.** 33% against 30%. A number in the subheadline does nothing measurable. Use one when the sentence needs it, not because a rule says so.

**Short subheads are not penalised.** 16% against 19%. There is no floor effect. What matters is the ceiling: long wins, short is merely neutral.

**Pronoun lane switching is not a signal.** 51% against 46%. Half of everything switches lanes. Using "I" and "you" in one line is fine too, 7% against 0%, and the direction favours the best posts.

### The one that reversed

**Sharing words with the title is not a fault.** The worst posts share *fewer* long words with the title, not more, 74% against 61%. Repeating the title's nouns is mildly associated with the *better* posts. Repeat words freely. What must never repeat is the claim.

---

## The subheadline shape

```
SUBHEAD = [ SPECIFIC ] + [ CONSEQUENCE, UNRESOLVED ]
```

**Beat one** is countable, dated, named, physical, or a stripped list of what was not there. It earns the right to make the claim.

**Beat two** is what that does to the reader, stated as an outcome, mechanism withheld. Say what changes. Never say how.

**The kill test.** If the subheadline could be the first line of the body, it is a summary and it fails.

Real examples from the corpus, highest engagement first:

```
977   My 2hrs/day biz made $247,347 this year (feel free to copy the system)
      I want to be transparent about what it takes to hit $50k months with a newborn.

277   Nobody Subscribed from My Notes (Until I Did This)
      How I Turned My Notes Into a Growth Machine Without Burning Out

262   Nobody Commented on My Posts. Until I Learned to Ask the Right Questions.
      I Thought My Readers Didn't Care. Until I Changed This One Thing.

199   99% of Creators Won't Make It in 2025 (Unless They Do This)
      Forget Algorithms: How to Win Big on Social Media in 2025

153   Substack is changing and most people will miss the shift
      If you're still building like it's Q2 2025, you're already behind.

140   Why I stopped trying to be "relatable"
      The performance of being a hot mess (and why I hate it)
```

---

## The headline shapes

Ten structures extracted by reading the top-performing titles and naming what repeated. **No control group.** This half is pattern observation, not measurement, and it is weaker evidence than the subheadline half above.

| Shape | Title formula |
|---|---|
| Nobody / Until | Nobody [did the thing you wanted]. Until I [small specific change]. |
| The Receipt | My [N hour] business made [$odd figure] this year (feel free to copy the system) |
| The Reset | If I lost it all today, here is exactly how I'd get back to [outcome] in [window] |
| The Subtraction List | [Odd N] things I stopped doing to [reach the outcome] |
| Institution on Trial | [Respected thing] is the worst [category] ever sold |
| Deadline Prophecy | Why [odd share] of [group] will be [bad outcome] by [year] |
| The Hidden Lever | The [thing] playbook that [odd share] of [group] ignore |
| The Unsee | I can't [ordinary activity] like a normal person anymore |
| The Tuition Receipt | What I wish I knew before [the thing they are about to do] |
| The Client Mirror | [He or she] [got odd result] in [short window] |

The bracket on the end of a title does real work in this corpus and appears in the highest performers: permission `(feel free to copy the system)`, the turn `(Until I Did This)`, the condition `(Unless They Do This)`.

---

## What she does with numbers

Measured from the top 50 in `data/corpus.json`, and cross-checked against her live archive.

### Where the figure sits

| | count of top 50 |
|---|---|
| Title carries a figure | 29 |
| Subheadline carries one | 17 |
| Both | 14 |
| **Neither, anywhere** | **18** |

**36% of her best posts contain no digit at all.** That is not a gap in the data, it is a lane: 277, 262, 140 and her three most recent posts all live in it. When she has no receipt she switches engine rather than reaching for a vaguer number.

### Odd is a receipt, round is a claim

```
$247,347   45,000   38.9K   953   $15,000   $1,700   27   17
```

Every one of these is a figure somebody looked up. `$300K`, `100K`, `70k` and `$50` are round and read as claims instead. The test is not trailing zeros, it is how much survives once the zeros come off: `300` leaves `3`, `1,700` leaves `17`. Her single biggest post carries the single most precise number in the corpus.

### A figure alone does nothing

`MONEY RECEIPT` has 49 uses and sits at **+3** against her median. The lift comes from dividing one number by another:

- `2hrs/day` → `$247,347`
- `10 systems` → `38.9K subscribers` → `in 4 months`
- `7 mistakes` → `8 months` and `€50K`
- `600 subscribers` → `$1,700`

Small input over large output. One number is a statistic. Two is a claim about leverage.

### The one number she invents

`99% of writers ignore`. `95% of "Full-Time Creators"`. The crowd claim is the only figure in the corpus with no ledger behind it, and it is always about other people, never about her own results.

---

## Honest limits

The engagement figures are likes, comments and restacks. Not opens, not clicks, not sales. The weak bucket contains admin posts that were never going to be liked, so this is correlation with a known confound rather than a controlled test. 198 pairs is a small sample and a 10-point gap on that base is suggestive, not proven.
