---
name: build-knowledge-base
description: Turn a client's source documents — brand book, sales deck, competitor analysis, market research — into a usable knowledge base. Use at the start of a project, when new source material arrives, or when you need to know whether a claim can be published. Produces a two-layer KB and a claim-evidence register.
---

# Building the knowledge base

The first thing to build and the thing everything else inherits from. Get this
wrong and every post downstream repeats the mistake.

## 1. Read everything before writing anything

Extract the text first — `pdfplumber` for PDFs, `python-pptx` for decks — and read
it properly. Do not skim and start summarising. The most valuable findings on the
original project came from noticing that two documents disagreed, and you cannot
notice that while reading one of them.

## 2. Two layers, and the wall between them matters

| Layer | Holds | Rule |
|---|---|---|
| `kb/` | Canon. What the product is, who it is for, what may be said. | Written as though a customer might read it. |
| `internal/` | The claim register, open contradictions, leadership rulings. | **Never quoted into anything outward-facing.** |

The separation is not tidiness. `internal/` is where you record that a headline
number is unsourced — and that record is exactly what must not appear in a post.
Keeping it in a separate tree makes the mistake structurally harder.

## 3. Build the claim-evidence register — this is the highest-value artefact

Go through every externally-usable claim in the sources and rate it:

| | Meaning | How to handle |
|---|---|---|
| ✅ | externally cited | Safe with the citation attached |
| 🟡 | vendor-published | Usable, but attribute rather than assert |
| 🟠 | internal estimate | Present as an estimate with assumptions visible |
| 🔵 | aspirational | Never state in the present tense |
| 🔴 | unsubstantiated | Qualify as a target, substantiate, or drop |

**Expect the result to be uncomfortable.** On the original project 33 of 62 claims
carried no citation, and the deck's single load-bearing economic figure was
contradicted two slides later by the same deck. That is normal for pre-launch
material and it is much cheaper to discover here than from a prospect.

Give every entry: where it is used, the risk if challenged, and what would
substantiate it. The last column is what makes the register actionable rather
than a list of complaints.

## 4. Run an adversarial pass over your own findings

Then have a second reviewer try to **refute** each finding, defaulting to refuted
when uncertain. On the original project this returned a verdict of
*partly-wrong*: several findings were overstated and two were simply incorrect,
including one already reported to the client. Preserve both passes — the
correction is part of the record.

## 5. Record contradictions rather than resolving them

Where the sources genuinely disagree, you do not have the authority to pick. Write
the question down, put the options and the trade-offs beside it, and get a ruling.
Then `internal/decisions-log.md` outranks everything, including your own judgement
and anything already written in `kb/`.

Keep that document short and keep it obeyed. A ruling that gets quietly relitigated
six weeks later is worse than no ruling.

## What good looks like

- A reader can answer "may we say X publicly?" from the register in under a minute
- Nothing in `kb/` contradicts a ruling
- Every number that reaches a draft has a rating behind it
- The source documents are treated as read-only; web research is supplementary and
  never overrides them
