# Company profile schema

What a profile must answer before the engine can score anything, and **why each field earns its
place.** A field that does not change a decision does not belong here.

Nine sections. Sections 3, 8 and 9 are the ones that make this a framework rather than a template,
and they are the three most likely to be filled in lazily.

---

## 1. Identity

Company, what it sells, to whom, at what price band, and in which geographies.

**Why it earns its place:** price band and geography change the answer more than industry does. A
40 lakh purchase and a 400 rupee subscription are not the same decision even inside the same sector,
and content that works in one market routinely fails in another for reasons that have nothing to do
with the subject.

## 2. Buying model

One of: PLG, SLG, PLS, enterprise or capex purchase, channel or distributor led. Plus cycle length,
typical deal size, and whether a committee or an individual decides.

**Why it earns its place:** this determines what content has to *achieve*, which is upstream of
everything.

| Model | What content must achieve |
|---|---|
| PLG | Get one person to self-serve and reach value |
| SLG | Get a committee to shortlist, then arm an internal champion |
| PLS | Get existing users to the point where sales is welcome |
| Enterprise or capex | Survive procurement, engineering and finance review |

**Most published content advice is written for PLG SaaS.** It reads plausible everywhere and
transfers badly, which is the single most common reason a content strategy underperforms without
anyone being able to say why.

## 3. Objective and weights

**The hard one, and the reason this is a framework.** *(Vatsal, 11 Sep 2026: this "needs to be
catered to specifically for every industry and company".)*

Not "what do you want from content". Every company answers that with everything. The profile records:

- **Ranked objectives**, at most three, in order
- **The weight split** across them, summing to 100
- **What the company is willing to give up** to get the top one
- **The date and who decided**, because objectives change and a stale objective is worse than none

**Method is in `docs/02-objective-elicitation.md`**, because almost nobody can answer this cold and
a form does not fix that.

**Worked example:** see `profiles/example-meridian.md`, where two objectives are weighted 65
and 35 and the sacrifice test is accepted. **Every number in that file is invented**, because a
corpus median measured on somebody else's audience tells you nothing about yours.

**Every objective that carries a weight must also declare a `kind`**, either `capture` or
`create`. The engine cannot know what a plant conversation is and must not guess, so `kind` is
the one field that lets a company-specific objective drive a company-agnostic scorer.
`engine/profile.py` refuses a profile without it rather than falling through to a default.

## 4. Audience

Who decides, who influences, who can block, and who merely reads. Named roles, not personas.

**Why it earns its place:** the blocker is usually invisible in content planning and usually decisive.
In industrial purchases the engineering reviewer and the safety officer can each kill a deal without
ever being a target reader. Content that never addresses them loses deals in a way that never shows
up in engagement numbers.

## 5. Channels

Which are in use, who owns each, cadence, and **whether the company's numbers on that channel are
measured or assumed.**

**Why it earns its place:** an unmeasured channel cannot contribute to Lift and the engine must know
that rather than inventing a baseline for it.

## 6. Claim regime

What may be said, what is barred, what needs clearance and from whom, and where the authoritative
source for specifications lives.

**Why it earns its place:** this is the Gate, and it is binary. In regulated, safety-relevant or
certification-bound industries a wrong claim is a commercial and legal exposure rather than a style
error. **The engine refuses to score a candidate whose claims cannot be sourced.**

## 7. Corpora

Pointers to: the company's own published content, its competitor set, and any measured engagement
data. With sizes and dates.

**Why it earns its place:** Lift is computed from the company's own corpus. **No corpus means no
Lift, and the engine must say so** rather than substituting industry benchmarks and presenting them
as the company's own.

## 8. Observable metrics

Two lists, both explicit.

- **Observable:** every metric this company can actually obtain, with its source and refresh cost.
- **Not observable:** what matters and cannot be seen. **The engine refuses to weight anything on
  this list.**

**Why it earns its place:** this is the honesty mechanism. Dwell time is the standing example, real
and reportedly decisive on LinkedIn and not exposed to a page admin in any usable form. Weighting an
unobservable produces a model that can never be checked, therefore never shown wrong, therefore not
a model.

**A profile with an empty "not observable" list has been filled in carelessly.** Every company has
things it cannot see.

## 9. Evidence status

Per profile: is this validated against measured data, or reasoned from the framework?

**Why it earns its place:** ruling 1 means both kinds will exist. The engine reports confidence
using this field, and **presenting a reasoned profile with the same confidence as a measured one
launders assumption into apparent fact.**

---

## Filling this in badly

Four failure modes, all seen in practice and all worth naming.

**Objectives that do not compete.** "Awareness, pipeline and recruitment, all important." Then no
weight can be derived and the engine cannot rank anything. Force the ranking.

**An empty "not observable" list.** Means nobody looked.

**A claim regime copied from the website.** The website is marketing copy. The claim regime is what
is *defensible*, which is usually narrower and lives with legal, engineering or the founder.

**A competitor set chosen by reputation.** It should be the companies this one actually loses deals
to, which is frequently a different list and occasionally an uncomfortable one.
