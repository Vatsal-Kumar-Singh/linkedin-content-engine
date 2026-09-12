# Architecture: the engine and the profile

**One rule decides where anything goes.** If it would still be true for a company in a different
industry with a different buying model, it belongs in the engine. If it is true about one company,
it belongs in that company's profile. **Anything ambiguous goes in the profile**, because a wrong
guess there costs one company, and a wrong guess in the engine costs every company quietly.

---

## The engine

Universal mechanics. Knows nothing about any industry, product or market.

### 1. The buying-job classifier

Takes a candidate piece and returns which job it does for a buyer. Jobs are drawn from the primary
research rather than the funnel folklore: problem identification, solution exploration, requirements
building, supplier selection, validation, and consensus creation across a buying group.

**Two things the engine must get right that most implementations do not.**

**A piece can do more than one job, and the classifier must say so.** Forcing a single label is what
makes these systems feel arbitrary. A case study does supplier selection and validation at once.

**The honesty gate carries over from the existing archetype work.** If more than 15% of a corpus
lands in "other", the taxonomy is wrong and the engine says so rather than quietly absorbing the
error. That gate has already caught a real taxonomy failure in this codebase's history and it is
cheap to keep.

### 2. Fit, Lift and Gate

Three separate outputs. Never averaged into one.

| | Question it answers | Fails when |
|---|---|---|
| **Gate** | May we publish this at all | A claim is unsupported, uncleared or barred. **Binary, runs first** |
| **Fit** | Is this the right thing to say, to this audience, for this job, on this channel | The subject is wrong for who is reading, or the ground is saturated |
| **Lift** | What is this treatment worth, measured on this company's own corpus | The subject is right and the format, length or author wastes it |

**Kept separate because they fail differently and the fix differs.** High Lift and low Fit is a
popular irrelevance. High Fit and low Lift is the right subject buried in the wrong format, which is
the most common failure in real feeds and the cheapest to correct. One blended score hides both.

**Weights live inside Fit and Lift, never across them**, and they come from the profile.

### 3. The measurement harness

Computes Lift from a company's own corpus rather than from published best practice. Needs:
per-author baselines, format and length bands, archetype indices normalised per author, and
saturation by theme against a competitor corpus.

**Normalising per author is not optional.** Raw medians rank the person, not the format. In this
codebase, raw medians once ranked one archetype first and another near last, and both readings
inverted once each post was scored against its own author's median. An engine that skips this step
will confidently tell a company to copy whoever has the largest following.

### 4. Channel adapters

The core stays fixed; adapters carry what differs per channel. An adapter declares the observable
metrics, the format vocabulary, the length bands, and whether its numbers are measured or borrowed.

**An adapter must declare its evidence status.** "Measured on this company's corpus" and "assumed
from another channel" are different claims and the output has to distinguish them. Format findings
in particular do not transfer between channels: in the measured corpus here, video is among the
weakest formats on a personal profile and among the most-used on company pages.

### 5. Validation

Score content that has already been published, compare against what it actually did, report the hit
rate **and the misses**. A scoring system never tested against outcomes is a spreadsheet with
opinions in it.

---

## The profile

Everything true about one company. Full field list and reasoning in `profiles/_schema.md`.

In summary: what they sell and to whom, the buying model, the objective and its weights, the
audience and who can block a deal, the channels in use, the claim regime, pointers to their corpora,
and **the list of metrics that are actually observable for them.**

---

## The part most frameworks skip: what is not observable

**Every profile declares what it cannot measure**, and the engine refuses to weight anything on that
list.

The motivating case: **dwell time.** Real, reportedly the strongest ranking signal on LinkedIn, and
**not exposed to a page admin or profile owner in any usable form.** Weighting it produces a model
that can never be checked against outcomes, which means it can never be shown wrong, which means it
is not a model. The same applies to most "authority" metrics and to any figure a company buys from a
tool that will not say how it is computed.

**This is a feature, not a limitation.** A framework that states its instrument list is auditable. A
framework that quietly proxies unobservables is astrology with a spreadsheet.

---

## Confidence, and why the engine has to report it

Ruling 1 means profiles will differ in how well grounded they are. Industrial B2B can be validated
against a measured corpus; SaaS and PLG profiles cannot, yet.

**So every recommendation carries its evidence status**, at minimum: measured on this company's
corpus, measured on a comparable corpus, or reasoned from the framework. **An engine that presents
all three with equal confidence is worse than no engine**, because it launders assumption into
apparent fact, and the user has no way to tell which is which.

Mechanism not yet designed. Recorded as open in `00-decisions.md`.

---

## Build order, and why this order

1. **Profile schema**, because everything reads from it and getting the fields wrong is expensive
   later.
2. **Objective elicitation**, because the weights are meaningless before it and most companies
   cannot answer it cold.
3. **Buying-job classifier**, validated against the corpora already held.
4. **Fit, Lift, Gate**, with a backtest.
5. **Channel adapters**, each declaring its evidence status.

**Steps 1 and 2 are what make this a framework rather than one company's tool.** They are also
the two most likely to be skipped under time pressure, which is why they are first.
