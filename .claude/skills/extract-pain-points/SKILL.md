---
name: extract-pain-points
description: Turn source documents into a plain-English pain point register the content engine can use. Use after building the knowledge base, when rewriting pain points, or when copy across the project reads like a strategy document instead of an advert. Covers the wording rules and the problem/value split.
---

# Extracting pain points

Everything downstream inherits its language from this file, so the rules live
here rather than in the templates.

## The register's shape

One row per pain, grouped into families:

| ID | The problem, plainly | What we do about it | Source |
|---|---|---|---|

Mark the strongest pain in each family. It stands in for the family when you are
holding message constant and testing something else.

## Three wording rules

**1. Say the subject word.** A reader scrolling past has two seconds. If the noun
that tells them this is for them is not in the headline, they do not know. A small
category label in a corner does not count — nobody reads the corner. On LinkedIn
this is also how the post gets distributed, since the algorithm classifies from
the copy.

**2. Write it the way you would say it out loud.** If you would not use the phrase
in a pub, it does not go on a card. Keep a translation table beside the register:

| Don't write | Write |
|---|---|
| the commercial model | what you pay |
| institutional knowledge | what your team learned |
| statement of work | the next invoice |
| time to value | how long before it does anything |

Extend it with whatever your sources are full of. The consultant register is
seductive because it is what the deck sounds like.

**3. One idea, short words.** If a sentence needs a second read, it is not
finished.

## The failure this file exists to prevent

Both columns must be concrete. The common pattern — and the one that survived
review twice on the original project — is a **sharp problem beside a vague
answer**:

> ✗ *Everything your consultants learned about your setup leaves when they do.*
>   → *What the system learns about your org, it keeps.*

The left side is a scene. The right side names nothing: which system, learned
what, kept where. Rewrite until a reader could hold you to the right column.

> ✓ *You never explain your setup twice. The system that runs it already knows.*

**Check the value column separately.** It is written last, gets less attention,
and is where the abstraction hides. Read the right column on its own, top to
bottom, and ask which of them you could put in a contract.

## Two traps

**Do not let a value statement claim a tier-gated feature as universal.** If the
answer only exists in the top pricing tier, either say so or write an answer that
is true at every tier.

**Do not put an unsourced number in a pain.** Check the claim register first. A
number describing the *reader's own situation* ("four vendors touch your stack")
needs no citation because it is not a claim about you — that is the safe pattern.

## Then sync it

The register is a document; the engine reads a config. Write the sync script and
a test that fails when they drift, before you need it. On the original project
the config never received either rewrite, and the model was fed superseded copy
for weeks with nothing detecting it.
