# Standing this up for a company that is not yours

**The order the pieces go in, what each one decides, and where each one usually goes wrong.**

Everything here exists in the repository. The skills in `.claude/skills/` carry the method for
each step in detail; this is the sequence they belong in and the reasoning for that sequence.

**Read this once before starting.** Most of the expensive mistakes in this repository's history
were order-of-operations mistakes: writing the style guide before measuring the corpus, planning
the calendar before knowing what content was for, building a gate before knowing what the claims
were.

---

## The shape

```
0  artefacts        get the raw material before asking anybody anything
1  what is true     pain points, claims, competitors, and YOUR OWN numbers
2  what it is for   objectives, weights, channels — the profile
3  what to publish  the calendar, scored rather than assumed
4  produce          draft, gate, judge, render, critique
5  learn            measure what shipped and feed it back
```

**Phases 0 and 1 are most of the work and produce nothing publishable.** That is normal, and a
project that skips them produces confident output nobody can defend.

---

## Phase 0 — Ask for artefacts before asking for answers

**People describe their company in marketing language and describe their documents accurately.**
`docs/decision/INTAKE.md` lists ten artefacts ranked by what they unlock per minute of effort.

| Get | Unlocks |
|---|---|
| **Recorded sales or demo calls, 3 to 5** | **The highest-value item by a distance.** The buyer's own words, the objections that really come up, who else is in the room |
| Investor or pitch deck | The real positioning and the claims they will make to people who do diligence |
| Lost-deal notes | Who blocked it and why. Usually the content gap nobody has named |
| Brand book | Claims discipline, what is barred, who signs off |
| Existing content with performance | **The Lift baseline.** Without it the scorer cannot compute Lift for this company at all |

**If you can only get one thing, get the call recordings.** And if you cannot get those, do not
wait: a five-minute voice note recorded straight after a call, by whoever was on it, answering
only *what did they actually say about what worries them*, sits one rung below a transcript and
costs the person who was already in the room five minutes.

**The trap.** Everything below a recording is somebody's account of buyer words rather than buyer
words. A sales-team interview is second best and is already a summary. **Account research you
wrote yourself is not buyer evidence at all**, and a profile that treats it as such has recorded
your own assumptions back to you.

---

## Phase 1 — Establish what is true

Four workstreams. The first three have skills; the fourth is the one people skip.

**Pain points** → `.claude/skills/extract-pain-points`. What the buyer actually suffers, in their
words, with what you do about it kept in a separate column. The register becomes
`engine/config/registry.yaml`, and the generator reads the config rather than your markdown.

**The claim register** → every externally-usable claim, its evidence, and its tier. This is what
`Gate` enforces later. **Write it before drafting, not after**, or the first thing that happens is
a good draft dying on a claim nobody checked.

**The competitor corpus** → `.claude/skills/build-knowledge-base`. It is for learning patterns and
finding gaps, never for reusing anybody's text. It also produces the saturation counts that tell
you which themes are open ground.

**Your own numbers, and this is the one that gets skipped.** Export the company's own published
posts and run:

```bash
python scripts/measure_corpus.py posts.csv --channel <one channel>
```

It emits the `corpus:` block a profile needs, and **it enforces both traps below rather than
trusting you to remember them**: it refuses to pool two channels, it scores every post against
its own author's median before aggregating, and it leaves out any band or format with fewer than
five posts instead of shipping an anecdote as a measurement. `scripts/example-posts.csv` shows the
input shape.

Without this, Lift has nothing to work from and the engine will tell you so rather than guessing.

**Two traps here, both costly.**

**A median computed across authors ranks the author, not the method.** One company's executives
can outscore another's six to one on employee base alone. Compare each author against their own
median, or the engine will confidently recommend copying whoever has the biggest following.

**A channel's medians never transfer to another channel.** Company page and personal profile are
different products with different audiences, and borrowing one for the other is an error this
repository has made and corrected.

---

## Phase 2 — Establish what the content is for

**This is the phase that has no deliverable and decides everything downstream.**

Run the elicitation: `docs/decision/OBJECTIVES.md`. Eight steps, roughly forty minutes per person,
run with each stakeholder **separately** — in a group the most senior answer becomes everybody's
within about ninety seconds, and you have learned one opinion at the cost of three sessions.

Write the result into a profile: `engine/decision/profiles/_schema.md` for the shape,
`engine/decision/profiles/example-meridian.md` for a filled-in one.

**Before you run it, ask what the channel will be made out of.** If a body of published work
already exists — articles, talks, posts — read that instead. **A back catalogue is revealed
preference and it beats a stated objective.** Elicitation earns its place where there is no track
record to read.

**The question that does the work** is not "what do you want". It is *"to get more of your top
objective, what are you willing to accept less of?"* An objective that costs nothing is not an
objective, and weights that come back near-equal mean nobody has chosen.

---

## Phase 3 — Decide what to publish

**Generate the calendar, do not write it.** `.claude/skills/build-content-calendar`. The grid is
pains × jobs × formats; hand-maintaining it guarantees it drifts from the register, and then two
documents disagree with nothing saying which is current.

Score it with `engine/decision/`:

| | |
|---|---|
| **Gate** | May we publish this at all. Binary, first |
| **Lift** | What this treatment is worth, from the corpus measured in phase 1 |
| **Fit** | Is it the right thing to say, given phase 2 |

**Backtest before you let it drive anything.** Score a calendar a person built with context and
compare. Agreement earns the right to automate; disagreement is a question worth answering, in
either direction. **The hand-built calendar is the test set, not the target.**

**The trap that cost the most.** An uncovered category reports as **zero**, and a zero reads like
a finding. A first run reported no bottom-of-funnel content anywhere and it was written up as a
strategic gap — when two thirds of one channel's angles had no mapping, and the unmapped set
happened to contain every late-stage angle there was. **Print what the classifier could not
classify before believing any zero**, and watch the unclassified rate: above roughly 15% the
taxonomy does not describe this corpus.

---

## Phase 4 — Produce

`ENGINE_FORCE_MOCK=1 python run.py --post <spec>` runs the whole loop with no tokens.

```
generate → deterministic gates → independent judge → revise → render → design critic
```

`.claude/skills/linkedin-post` for the copy, `.claude/skills/creative-direction` for the visual
work, `.claude/skills/content-gauntlet` for extending the gates.

**The judge must be a different model family from the generator.** Self-preference bias is real: a
judge favours phrasing that sounds like itself, which is exactly the tell the rubric exists to
catch. The engine refuses to run both on one family unless you override it deliberately, and
stamps any such run `judge_independence: DEGRADED`.

**Rendering is verified by looking.** Several defects in this repository passed every test and
were caught only by opening the PNG. Render it, open it, look at it — then look again with real
copy on it.

---

## Phase 5 — Learn

Measure what shipped, feed it back into the corpus from phase 1, and let Lift change its mind.

**Expect your own data to contradict the published benchmark.** On one project it happened five
times: subject-line length, video performance, which account to model, which archetype was
strongest, and copy length. Every time, the benchmark was real and measured on somebody else's
audience. **Measure before you believe.**

---

## The rules that run through every phase

**A success message is not evidence.** A zero exit code proves the tool ran, not what it ran on.
Verify the effect — grep the output for the exact thing you changed.

**A green suite is not evidence either.** After adding a guard, break the thing it guards and
confirm it fails. `python scripts/mutation_check.py` does this for the shipped guards; it found
one that had never protected anything. `.claude/skills/verify-your-tests` is the method.

**Refuse rather than default.** Where an input is missing, return nothing and name it. A plausible
number computed from nothing is worse than an honest gap, because **the gap is the only thing that
tells anybody the input was never gathered.**

**Canon lives in exactly one place.** Do not copy a document nearer to where you are working.
Whoever opens the nearer one reads the wrong version and nothing tells them.

**Put quality floors in code, not in a style guide.** Contrast ratios, length bands, banned words
and legibility minimums belong in a checker that runs. A style guide is a suggestion; a failing
check is a decision.

---

## What this repository does not do for you

**It does not know your claims.** The claim register is real work and nobody else can do it.

**It does not have your numbers.** `engine/decision/` ships with no measurements on purpose, and
will decline to score until a profile supplies them.

**It does not decide.** Every score arrives with its components and its gaps so that a person can
disagree with it. That is the design, not a limitation.
