# linkedin-content-engine

A content pipeline for B2B products that refuses to publish its own bad drafts.

You give it source material — a brand book, a sales deck, competitor research —
and a set of pain points. It writes LinkedIn posts, renders the creative, and puts
every draft through a loop that tries to reject it before a human ever sees it:

```
generate → deterministic gates → independent judge → revise → render → design critic
```

Before any of that, it can tell you **what to publish and why**:

```
intake → company profile → Gate / Lift / Fit → channel split → calendar
```

That half ships with **no measurements of its own**. It reads them from a profile you fill in from
your own corpus, and where the profile is silent it returns nothing and says which input is
missing, rather than scoring you against somebody else's audience.

**Setting it up for a company is `docs/PLAYBOOK.md`** — six phases, what each one decides, and the
trap in each. The first two produce nothing publishable and are most of the work.

**What the advice is grounded in is `docs/BENCHMARKS.md`** — 3,141 LinkedIn posts from 77 B2B
companies, every one read and labelled by hand, cut by what you sell, how you sell it, who buys,
how big you are and which industry you sell into. `docs/CELLS.md` cuts the first three at once and
names exemplars per cell.

**Where the project actually stands, including what is unfinished and what it would take to
finish, is `docs/STATE.md`.** Read it before picking any of this up. It also carries the mistakes
that cost the most time, which is the part most worth not repeating.

It ships with a fictional example product, so a fresh clone renders something
immediately. Swap the config for yours and it is your engine.

---

## Try it in two minutes

```bash
cd engine
pip install -r requirements.txt
python -m playwright install chromium

ENGINE_FORCE_MOCK=1 python run.py --post example_01
```

Mock mode runs the whole pipeline — generation, validation, judging, rendering,
the design critic — on fixture copy, with no API key and no tokens spent. Every
artefact is stamped `mock: true` so it can never be mistaken for a real run.

**The example run ends in `HUMAN_REVIEW` with gate failures, on purpose.** The
mock fixtures include deliberately bad copy so you can watch the gates catch it.
That is the system working, not failing.

To render the creative templates without running the pipeline at all:

```bash
python scripts/build_examples.py     # every card template, light and dark
```

---

## Making it yours

Four files, in this order. Nothing is hard-coded in a template — edit these and
everything restyles.

| File | What it holds |
|---|---|
| `engine/config/registry.yaml` | Your pain points, families, personas, wordmark, brandline |
| `engine/config/brand.yaml` | Palette, typography, formats, legibility floors |
| `engine/config/claim-rules.yaml` | The gates. Structural ones ship; your claim gates go in the marked block |
| `engine/prompts/generator.md` | Voice. Replace `{{SUBJECT}}` and `{{COMPANY}}` |

Two things worth changing deliberately rather than by accident:

**The subject word.** Gate `C0.1` requires a noun in every headline that tells the
reader the post is for them. It is not only a copy rule — on LinkedIn the
algorithm classifies a post from its copy, so that word is also how the post gets
distributed.

**Your claim gates.** `claim-rules.yaml` has a marked block where the original
project's claim-specific gates lived. Write one gate per claim you cannot afford
to publish wrong. See the `build-knowledge-base` skill for how to work out which
those are.

---

## The skills are the substance

`.claude/skills/` carries the method, not just the code. Each was written from
something that actually went wrong.

| Skill | Use it when |
|---|---|
| `build-knowledge-base` | Source documents arrive. Two-layer KB, claim-evidence register, adversarial review |
| `extract-pain-points` | Turning sources into a plain-English register. The wording rules |
| `build-content-calendar` | Planning what to publish. Tier discipline, runway arithmetic |
| `linkedin-post` | Writing one post. Hooks, hashtags, image-versus-caption |
| `creative-direction` | Building a visual system. Measuring a reference, light/dark, motion |
| `content-gauntlet` | Extending the quality loop. Judge independence, gate design |
| `verify-your-tests` | After adding a guard. Mutation testing |

---

## What is in the box

```
engine/
  postengine/       generator, validators, judge, renderer, animation
  config/           the four files above, plus engine.yaml and rubric.yaml
  templates/        7 card layouts + 1 carousel, one shared visual ground
  prompts/          generator, revision, judge, design critic
  posts/example/    three worked specs
  scripts/          preview a card, render every template, mutation-check the suite
  tests/            unit tests, plus a mutation harness
```

The creative system: a pale two-pole gradient ground with one of seven open-shape
motifs drawn over it, in light and dark, with optional motion. Geometry is seeded
from the post id so a card renders identically every time.

---

## Providers

Set `ANTHROPIC_API_KEY` and/or `OPENAI_API_KEY`, or point `engine.yaml` at the
`claude_cli` provider to drive a logged-in CLI with no key at all.

Generator and judge should be different model families — a model favours phrasing
that sounds like itself. When they are not, the run is stamped `PARTIAL` or
`DEGRADED` rather than `INDEPENDENT`. That label is deliberate: an honest stamp is
worth more than a flattering one.

---

## Requirements

Python 3.11+, `pyyaml`, `playwright` (Chromium). Optional: `ffmpeg` for MP4 motion
export — without it, loops encode as GIF.

## Licence

MIT. The example product, its pain points and its palette are fictional.

---

## Credit

The engine's original architecture — the gauntlet loop, the deterministic
validator, the template renderer and the `/save` command — was built by
**Raunak Jain**. This repository is a generalised version of that work with the
client-specific content removed, developed further across two creative passes
and a set of skills capturing the method.
