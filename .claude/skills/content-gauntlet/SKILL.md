---
name: content-gauntlet
description: Set up or extend the quality loop — generator, deterministic gates, independent judge, revision. Use when adding a validation rule, wiring a model provider, changing the pass thresholds, or diagnosing why bad copy reached a human. Carries the failure modes that let unchecked copy through.
---

# The gauntlet

Generate → validate deterministically → judge independently → revise. The point is
that no draft reaches a human without something having tried to reject it first.

## The three stages do different jobs

| Stage | Catches | Nature |
|---|---|---|
| **Deterministic gates** | Rules with a right answer — banned phrases, missing subject word, unqualified numbers | Regex and structure. Fast, free, never wrong about what it checked. |
| **Independent judge** | Judgement — does the hook work, is this one idea or three, does it read as human | A model, scored against a rubric. |
| **Human** | Intent, taste, anything the register flags | Last. |

Put a rule in the gates whenever it *can* go there. A gate that fires is worth
more than a judge that might.

## Judge independence, and how to be honest about it

The judge must not see the generator's private reasoning, its self-assessment, or
the deterministic findings. Show it the draft and the rubric. Anchoring it on what
the validator already found destroys the second opinion you are paying for.

Ideally the judge is a different model family from the generator — a model
favours phrasing that sounds like itself. When that is not possible, say so:
stamp each run `INDEPENDENT`, `PARTIAL` (same family, different model) or
`DEGRADED` (same model judging its own voice). An honest label is worth more than
a flattering one.

## What the revision packet may contain

Problems and replacement wording. **Not scores.** Hand a generator a number and it
argues with the number instead of fixing the text.

Also list the criteria that *passed*, by identifier only. Without that, a revision
fixes the named failure and breaks something adjacent — observed directly: a draft
cleared one criterion and broke two others, because the packet only ever named
failures.

## Ship the best draft, not the last

Iteration is not monotonic. A fourth attempt can be worse than the third. Rank the
iterations and render the winner — and never let a draft that trips a gate win on
score, however well the judge liked it.

## Failure modes that let bad copy through

These all happened. Each is cheap to check for and invisible once shipped.

**A gate satisfied by another gate.** One gate required the subject word in every
headline. A second gate — meant to catch headlines that mean nothing alone —
listed that same word among its acceptable concrete nouns. It could never fire.
When you add a rule, check it cannot be trivially satisfied by one that already
exists.

**Text composed at render time never reaches the validator.** A card eyebrow built
from config at render time bypassed every gate and shipped banned language onto
finished creatives. If on-card text is not a draft field, no gate can see it.

**The model reads config, not your document.** The generator's brief pulls pain
titles and values from a config file, not from the markdown you edited. Two
rewrites never reached it. Write the sync script and a drift test.

**A green suite proves nothing on its own.** Break each guard deliberately and
confirm it fails. See the `verify-your-tests` skill.

## Calibration before enforcement

Run in calibration mode first: record the thresholds, do not enforce them.
Hand-score a sample and compare. Published pass marks — "80% of binary checks",
"9 of 12 scored" — are guesses until you have checked them against a human on
your own content.

## When you add a gate

1. Write it, with a `message` saying what is wrong and a `fix` saying what to do
2. Test it against strings that should pass **and** strings that should fail
3. Check it is not already satisfied by another gate
4. Break it and confirm the suite notices
