# Profile: Meridian (worked example)

**Every number in this file is invented.** Meridian is the fictional data-observability product
the rest of this repository demos with. The profile exists so a fresh clone can run the decision
layer end to end and see the shape of a filled-in answer.

**Do not copy the numbers. Copy the structure.** A corpus median measured on somebody else's
audience — real or imaginary — tells you nothing about yours. The engine ships with no
measurements precisely so that this file cannot quietly become everybody's default.

Schema and the reasoning behind each field: `_schema.md`.

---

## 1. Identity

Data observability for analytics teams. Software, sold as a subscription.

## 2. Buying model

**B2B SaaS, sales-assisted, annual contract.** A team can trial it without talking to anybody, and
anything above a certain seat count goes through procurement.

The consequence that shapes everything below: **the reader is often not the buyer.** An analytics
engineer finds the product, and a VP of Data signs for it. Content therefore has to survive being
forwarded by somebody who will not be in the room when it is discussed.

| Role | What they do to a deal |
|---|---|
| VP Data / Head of Analytics | Decides |
| Analytics engineer | Finds it, champions it, forwards it upward |
| Platform or infra lead | **Blocks.** Owns what else runs in the warehouse |
| Security review | **Blocks.** Never speaks to a vendor before the questionnaire |
| Finance | Approves. Asks what it replaces |

## 3. Objective and weights

*Elicited from one stakeholder. In a real profile that is a weakness worth recording, and the
method for doing it properly is in `docs/OBJECTIVES.md`.*

| Objective | Points | Horizon | Kind |
|---|---|---|---|
| Qualified trials from analytics teams | **65** | 1 to 2 quarters | capture |
| Known as the team that explains this problem well | **35** | 2 to 3 years | create |

**Sacrifice test: accepted.** Zero on the second for two quarters, to double the first.

## 4. Audience

See section 2. **The two blocking roles are the load-bearing part**: platform and security decide
deals, appear in no lead list, and never take a vendor call. Reaching them is a publishing problem
by construction.

## 5. Channels

Declared in the YAML block as `channels:`, because how many there are and who they belong to is
a fact about this company rather than about the engine.

| Channel | Kind | For |
|---|---|---|
| `page` | organisation | Validation. A visitor has already arrived; it cannot win reach |
| `founder` | person | Creation. Reaches people who do not follow the company |

A real profile with two named executives declares both. **They will carry the same buying jobs**,
and what separates them is mode — who speaks at events, who writes long form, who has
photographs — which sets format and source material rather than which jobs they do.

## 6. Claim regime

Nothing measured on a customer's data may be published without written clearance. No customer
named without it. No uptime or accuracy figure without the run behind it.

**These are constraints, not objectives.** They belong in the Gate and carry no weight.

## 7. Corpora

| Corpus | Size | Grounds |
|---|---|---|
| Own company page | 40 posts | Format baselines for the page |
| Founder's profile | 60 posts | Length bands and format medians |
| Competitor corpus | 900 pages, 6 themes | Saturation, and therefore openness |

## 8. Observable metrics

**Observable:** impressions, reactions, comments, reposts, follower count, per-post analytics,
trial signups with a source field.

**Not observable, and the engine refuses to weight any of it:**

- **Dwell time.** Not exposed to a page admin in any usable form
- **Who forwarded a post, and to whom** — which is exactly what consensus content is for
- **Whether a post reached a blocking role at all**
- **Attribution from a post to a trial**, beyond a self-reported field most people skip

## 9. Evidence status

| Component | Status |
|---|---|
| Lift | Invented for this example. In a real profile: measured, with the corpus named |
| Gate | The claim rules are real work. Write them before drafting, not after |
| Saturation | Invented. Real ones come from a competitor corpus you build |
| Objective weights | Stated, one stakeholder |
| Angle to buying job | **Inferred.** The weakest link in the scorer, in every profile |

---

```yaml
# MACHINE-READABLE. engine/decision/profile.py reads this block and nothing else in the file.
# EVERY NUMBER BELOW IS INVENTED. Replace them with your own or the engine is scoring fiction.
company: Meridian
example: true
elicited_on: 2026-01-01
stakeholders_run: 1
agreed_by: [the fictional founder]
review_on: 2026-07-01

company_type:
  offering: saas
  motion: PLS          # product-led, sales-assisted above a seat count
  buyer: practitioner  # who signs. Optional, and the axis that moves measured publishing
                       # behaviour most: practitioner-led pages run about 60% non-buying
                       # content, procurement-led pages about 32%. See docs/BENCHMARKS.md
  purchase: subscription

objectives:
  weights:
    qualified trials from analytics teams: 65
    known as the team that explains this problem well: 35
  # `kind` is the only thing the engine understands. The objective NAMES are yours.
  kinds:
    qualified trials from analytics teams: capture
    known as the team that explains this problem well: create
  horizons:
    qualified trials from analytics teams: 1-2 quarters
    known as the team that explains this problem well: 2-3 years
  sacrifice_test: {asked: "zero on the second for two quarters to double the first", answer: accepted}
  measured_by:
    qualified trials from analytics teams: "trial signups with a source field, which most people skip"
    known as the team that explains this problem well: "unsolicited conference and podcast invitations"

# THE CHANNELS THIS COMPANY HAS, AND WHAT KIND EACH IS. The names are yours; the engine reads
# `kind` and nothing else. Two kinds exist because the distinction is structural: a named person
# reaches people who do not follow the company, and a page is read by somebody who already
# arrived. Declare as many as you have — three named people and a page is a normal shape.
channels:
  founder:
    kind: person
    seat: founder      # which seat, not just which kind. Measured against the company's own page
                       # in the same window, a founder ran 3.06x and a VP ran 0.54x -- a wider gap
                       # than person-versus-page. One of: founder, c-suite, vp, ic
    what: "creation. Reaches analytics engineers who have never heard of us"
  page:
    kind: organisation
    what: "validation. A visitor has already arrived; it cannot win reach"

channel_strategy:
  founder_network:
    viable: yes
    evidence: "INVENTED. In a real profile this is set from how many original posts they have
      actually written in the last twelve months, never from what they say they will do"
  category_awareness: emerging
  named_person_exposure: low

constraints:                 # Gate items. They carry no weight
  - no customer named without written clearance
  - no figure measured on customer data without clearance
  - no uptime or accuracy claim without the run behind it

# INVENTED. Yours come from measuring your own published posts: median engagement by word band,
# by format, on each channel separately. A channel's medians never transfer to another channel,
# and another company's never transfer to you.
corpus:
  length_bands:              # [min_words, max_words, median_engagement]
    - [200, 10000, 240.0]
    - [100, 199, 150.0]
    - [1, 99, 70.0]
  format_lift:               # per channel, because they differ and the difference is large
    # The personal profile rewards photographs, which is what most measured corpora show and
    # which no renderer produces. Those slots ship on TEXT with a note saying what to shoot.
    founder: {photo album: 400.0, single image: 200.0, text: 100.0, carousel: 500.0}
    # The page rewards designed work, which this engine does render. Two channels, two different
    # answers, from one profile: that is the whole reason format lift is measured per channel.
    page: {designed card: 300.0, carousel: 260.0, text: 120.0}
  saturation:                # competitor corpus chunks per theme. Low is open ground
    pipeline reliability: 40
    data quality: 320
    warehouse cost: 180
    observability tooling: 900

not_observable:
  - dwell time
  - who forwarded a post and to whom
  - whether a post reached a blocking role
  - attribution from a post to a trial

evidence_status:
  lift: invented for this example
  gate: reasoned
  saturation: invented for this example
  objective_weights: stated, single stakeholder
  angle_to_job: inferred
```
