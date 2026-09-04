# Build Plan

## P0 — demo-critical

| # | Item | State |
|---|---|---|
| 1 | Config layer — `engine.yaml`, `brand.yaml`, `claim-rules.yaml`, `rubric.yaml` + changelog | ✅ |
| 2 | Content specs for Round 1 (6 posts) extracted from `content-calendar.md` / `content-backlog.md` | ✅ |
| 3 | Schemas — draft, deterministic report, judge report, run report | ✅ |
| 4 | Deterministic validator compiling `claim-rules.yaml` → gate results | ✅ |
| 5 | Provider adapters — anthropic, openai, mock; registry with family-independence assertion | ✅ |
| 6 | Generator agent (structured output, revision mode) | ✅ |
| 7 | Judge agent with `JudgePacket` context firewall, reason-before-score | ✅ |
| 8 | Gauntlet orchestrator + run store + calibration/enforced modes | ✅ |
| 9 | `run.py` CLI with the console trace | ✅ |
| 10 | CARD templates: `big_number`, `comparison`, `insight` on a shared token system | ✅ |
| 11 | DOC template: `editorial` carousel (cover + body + close) → PNGs + PDF | ✅ |
| 12 | Renderer: Playwright w/ Chrome fallback, measured fit validation, auto-fit | ✅ |
| 13 | Design critic (vision) with bounded iterations | ✅ |
| 14 | Tests: claim rules, banned phrases, qualifiers, naming, scoring, pass/fail, max-iteration, malformed judge JSON, overflow, isolation | ✅ |
| 15 | End-to-end Round 1 run + rendered creative | ✅ |
| 16 | Hostile self-review; fix CRITICAL/HIGH | ✅ |
| 17 | README with reproducible instructions | ✅ |

## P0 — complete. See STATUS.md for the hostile-review findings and fixes.

## P1 — useful next

- Pairwise hook selection (generator emits 3 hooks; judge picks, both orderings averaged) — rubric §Judge design.
- Blind intent classification (open question 1): judge classifies cold, engine compares to declared tier.
- `calibrate.py` — hand-score capture, judge-vs-human agreement report, threshold derivation from the real distribution.
- Batch runner for a whole round with a session-limit-aware queue.
- Remaining templates: CARD `framework`, DOC `comparison` / `process`.
- Performance ingest CLI writing into `performance.json` and a cross-run comparison table.

## P2 — later

- Canva adapter behind the same template-router interface.
- Apify LinkedIn scrape for competitor anchor sets (needs token, Round 2+).
- Employee-advocacy reshare tracking.
- Multi-family judge council (3+ families, majority verdict).
