# Rubric Changelog

Every run stamps `rubric_version` into its report. Scores are only comparable
across runs that share a version. Bump the version for **any** change to a
criterion, threshold, or auto-zero list, and record it here.

Versioning: `MAJOR.MINOR.PATCH`
- **MAJOR** — a criterion added, removed, or redefined. Prior scores are not comparable.
- **MINOR** — anchors, examples or wording clarified. Prior scores are broadly comparable.
- **PATCH** — typo or reference fix. No scoring impact.

---

## 1.1.0 — 2026-08-26

Additions found necessary while building and hostile-reviewing the engine. No
existing criterion changed, so scores remain comparable with 1.0.0.

| Change | Why |
|---|---|
| Gate `S1` — spec integrity | A blocked or unregistered pain point is knowable before a token is spent. `B1` stays a **binary check**, because that is what the rubric says it is; spec integrity is a separate blocking concern the rubric does not cover. |
| Gate `A1.5` — replacement claim with no competitor named | Hostile review found "the product replaces your existing DevOps tooling" passing every gate. Ruling 3 withdrew the *claim*, not merely the naming of a rival. |
| Gate `A2.3` — the qualifier must be on the creative | A2 requires the qualifier on the image. Making `creative_qualifier` an explicit field means what the validator scans is exactly what the renderer draws — previously the chip was derived at render time and was never checked. |
| `first_comment` and `hook_alternatives` added to the scanned field set | Both reach a reader — the first comment publishes, and a human may promote an alternative hook. Neither was scanned. |
| A2 figure patterns cover word forms and loose spacing | "seventy percent" and "70  %" both evaded the numeric patterns. |
| `A5.2` engagement bait widened from caption to all fields | Bait on the creative was not caught. |

**Bugs fixed in the deterministic layer** (no rubric change): the A4 number
pattern placed `\b` after `%`, where it can never match, so `40%` escaped the
no-hard-numbers check.

---

## 1.0.0 — 2026-08-26

Initial machine-readable encoding of `engine/judge-rubric.md` as authored by Vatsal.

**Encoded as-is:** gates A1–A6 · binary checks B1–B11 · scored criteria C1–C4 · the
C3 auto-zero list · the C4 tick-mark-list anti-pattern · the C1 anchors.

**Engine additions, flagged as additions rather than silently folded in:**

| Addition | Why | Handoff ref |
|---|---|---|
| Gate `N1` — naming canon | Getting the company → the platform → the product wrong makes every post wrong. Mechanically checkable, so it belongs in code. | canon.md, ruling 2 |
| Gate `L1` — internal-material leak | `decisions-log` and `claim-evidence-register` are internal. A regex is a cheaper guarantee than trusting a model to remember. | HANDOFF "A note on the two layers" |
| Binary `B12` — CTA | The rubric has no criterion for "what should the reader do". | open question 5 |
| Deterministic pre-pass | The mechanical half of A1–A6, B1/B4/B6/B8, C1/C3/C4 now runs as regex before any model call. | open question 4 |
| `block_on_zero_brand_voice` | 9/12 is reachable as 3+3+3+0. Wired and defaulted **on** in `pass_rules`, but inert while mode is `calibration`. | open question 3 |
| Length-earns-nothing note in the judge prompt | Verbosity bias control. | open question 6 |

**Deliberately NOT resolved** (they are rubric-design decisions for a human):

- **Open question 1** — blind intent classification. C2 stays scored-and-advisory, which is
  incoherent as written. The fix costs an extra judge call per post; it is built as a P1 flag
  (`blind_intent_classification`), off by default, because turning it on changes what C2 means.
- **Open question 2** — thresholds. Not invented, not adopted. Mode defaults to `calibration`
  so nothing auto-passes on an uncalibrated number.
