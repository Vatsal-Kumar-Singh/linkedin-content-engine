# the product LinkedIn Content & Creative Engine — Architecture

**Status:** P0 build. **Owner:** engineering. **Last updated:** 2026-08-26.

The engine turns a *content spec* (a YAML file under `engine/posts/`, usually one
row of whatever calendar you keep) into a
human-review package: a LinkedIn post, a branded creative, and a complete audit trail
proving the draft was independently criticised and revised before a human saw it.

---

## 1. The two loops

```
                          ┌──────── COPY GAUNTLET ────────┐

  content spec  ──►  GENERATOR  ──draft──►  DETERMINISTIC  ──►  JUDGE  ──►  verdict
   (YAML)            (family A)             VALIDATOR           (family B)      │
                          ▲                 regex/schema        fresh ctx       │
                          │                 zero tokens         reason→score    │
                          └────── structured feedback only ────────────────────┘
                                          (max_iterations)
                                                 │
                                                 ▼
                                          HUMAN REVIEW
                                                 │
                          ┌──────── CREATIVE GAUNTLET ────┐
                                                 ▼
   approved copy ──► TEMPLATE ROUTER ──► HTML/CSS ──► Chromium ──► PNG/PDF
                                             ▲            │
                                             │            ▼
                                             │      FIT VALIDATOR  (measured overflow, deterministic)
                                             │            │
                                             └── DESIGN CRITIC (vision model) ──┘
```

Both loops share one rule: **the thing that makes the artifact never grades the artifact.**

---

## 2. Isolation — how the gauntlet is actually enforced

The requirement "generator and judge must not share context" is enforced in code, not by
convention. Three mechanisms:

| Mechanism | Where | What it guarantees |
|---|---|---|
| `JudgePacket` allowlist | `postengine/agents/judge.py` | The judge prompt is built **only** from a frozen dataclass with a fixed field set. Generator reasoning, self-assessment, prior judge scores and internal constraint docs cannot be reached from the judge call site. |
| Separate provider instances | `postengine/providers/registry.py` | Generator and judge get different `Provider` objects with separate clients, separate system prompts and no shared message history. Every call is stateless — full context is rebuilt per call. |
| Family check | `postengine/providers/registry.py:assert_independent` | Refuses to run with generator and judge on the same **model family** unless `allow_same_family: true`; when overridden the run report is stamped `judge_independence: DEGRADED`. |

The judge receives exactly: the draft's public fields, the rubric text + version, the
public-safe constraint digest, and the content objective. It never receives
`decisions-log.md`, `claim-evidence-register.md`, the generator's reasoning, or its own
previous scores.

`tests/test_isolation.py` asserts these properties against a canary string planted in
generator-private state.

---

## 3. Layer order — cheap and objective before expensive and subjective

1. **Schema** — the model returned valid JSON with the required fields (`models.py`).
2. **Deterministic validator** — `config/claim-rules.yaml` compiled to regex/predicates.
   Runs in milliseconds, costs nothing, cannot drift. Covers rubric gates A1–A6 and the
   mechanically-checkable half of B1/B4/B6/B8, C3 and C4.
3. **LLM judge** — subjective quality only: hook strength, intent tier, voice, humanness.

This is handoff open-question 4 ("the gates ask the judge to remember too much") answered
in code: **code evaluates objective constraints, models evaluate taste.**

---

## 4. Configuration surface

Nothing operational is hard-coded in application logic.

| File | Governs |
|---|---|
| `config/engine.yaml` | mode (calibration/enforced), thresholds, max iterations, providers, retries |
| `config/brand.yaml` | palette, typography, dimensions, interim the product sub-brand flag |
| `config/claim-rules.yaml` | every deterministic gate: banned strings, qualifier-required figures, naming rules, internal-leak strings |
| `config/rubric.yaml` | rubric version pointer + scored criteria weights |
| `RUBRIC_CHANGELOG.md` | append-only version history; the version string is stamped into every run |

Brand values are injected as CSS custom properties at render time from `brand.yaml`.
When the product sub-brand rules land, editing one file restyles every template.

---

## 5. Modes

**CALIBRATION (default).** Thresholds are recorded but never auto-pass. Every post exits
to `HUMAN_REVIEW` with its full score distribution attached. This is the handoff's
instruction — the existing 80% / 9-of-12 numbers are explicitly flagged as invented, so
the engine refuses to treat them as truth until 10 posts have been hand-scored.

**ENFORCED.** `pass_rules` in `engine.yaml` become binding. Includes
`block_on_zero_brand_voice` (handoff open-question 3) which is off by default only because
it is a rubric change leadership has not made yet — it is wired and one flag away.

---

## 6. Rendering

`STRUCTURED JSON → Jinja-free string templates → Chromium → PNG (+PDF for DOC)`

- Playwright when installed; falls back to the local Chrome binary via `--headless
  --screenshot`. Renderer availability is detected, never assumed.
- **Fit validation is measured, not guessed.** After layout, the page is queried for real
  element geometry (`scrollHeight > clientHeight`, line counts, computed font-size). Text
  that overflows triggers a bounded auto-fit down the type scale; if the required size
  falls below the mobile-legibility floor (`min_body_px`, rubric B9) the render **fails
  loudly** rather than shipping unreadable output.
- A pre-render character-budget check rejects absurd input before a browser starts.

## 7. Persistence

`runs/<run-id>/` holds `input.json`, `iteration_NN.json` (draft + deterministic report +
judge report per iteration), `judge_report.json`, `post.md`, `creative*.png`,
`run_report.json`, and `performance.json` (all-null skeleton for the outer loop).
Nothing is overwritten; the history is the product.
