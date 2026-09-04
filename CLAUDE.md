# linkedin-content-engine — working instructions

A content pipeline for B2B products, with a quality loop that tries to reject
every draft before a human sees it. Read `README.md` first for what it does; this
file is how to work on it.

**Start with the skills.** `.claude/skills/` carries the method — building the
knowledge base, extracting pain points, planning the calendar, writing a post,
developing the creative direction, extending the gauntlet, verifying the tests.
Each was written from something that actually went wrong on a real project. They
are more useful than reading the code.

---

## Rules

**1. Never invent a number.** Keep a claim-evidence register rating every
externally-usable claim, and check it before any figure reaches a draft. A number
describing *the reader's own situation* ("four vendors touch your stack") needs no
citation — it is not a claim about you. That is the safe pattern.

**2. Whatever your project's rulings document says, wins.** Above the knowledge
base, above the code, above your own judgement. Do not relitigate it.

**3. Internal material never goes outward.** Keep the register and the open
questions in a separate tree from the canon, so quoting the wrong one is
structurally harder.

**4. Plain English.** If a sentence would sound odd said aloud to a colleague, it
is wrong. Gate `C0.2` refuses a register of consultant phrases outright; extend
the list with whatever your own sources are full of.

---

## Getting oriented

```bash
cd engine
python run.py --list                                # available specs
ENGINE_FORCE_MOCK=1 python run.py --post example_01 # the whole pipeline, no tokens
python scripts/build_examples.py                    # every template, both grounds
cd tests && python -m unittest discover -s . -t .   # the suite
cd .. && python scripts/mutation_check.py           # do those tests test anything?
```

`ENGINE_FORCE_MOCK=1` runs everything on fixture copy and stamps each artefact
`mock: true`. The example run ends in `HUMAN_REVIEW` on purpose — the fixtures
include deliberately bad copy so the gates have something to catch.

---

## Things that will bite you

**Rendering is verified by looking, not asserting.** Several defects here passed
every test and were caught only by opening the PNG: a comet head detached from its
tail, a scrim correct on one ground and glaring on the other, a motif that read as
a bullseye. Render it, open it, look at it — then look again with real copy on it.

**Text composed at render time never reaches the validator.** The card eyebrow is
built from config during rendering, so it bypassed every gate and shipped banned
language onto finished creatives. If on-card text is not a draft field, no gate
can see it.

**A gate can be satisfied by another gate.** The gate meant to catch meaningless
headlines listed the subject word among its acceptable nouns — while another gate
already required that word in every headline. It could never fire. When you add a
rule, check it is not trivially satisfied by one that exists.

**The generator reads config, not your markdown.** Pain titles and values come
from `config/registry.yaml`. If you keep a document as your source of truth, sync
it and add a test that fails when they drift.

**A green suite is not evidence.** Two guards here passed while the thing they
named went unprotected. After adding a guard, run `scripts/mutation_check.py` and
confirm it fails when you break the thing.

**Prefer derived lists to hand-written ones.** Anything enumerating templates,
shapes or gates should read them from the filesystem or config. A hardcoded list
drifts out of reality while continuing to look correct.

**Every render must be byte-identical.** Geometry is seeded from the post id,
never the clock. Stills also freeze CSS animations before shooting — without that,
a still of an animated card samples whatever moment the screenshot landed on.

**Canon lives in exactly one place.** Do not copy a document nearer to where you
are working. Whoever opens the nearer one reads the wrong version, and nothing
tells them.
