#!/usr/bin/env python3
"""Which channel should carry which buying jobs, and whether the split applies at all.

**This is the part the framework was missing.** `research/03-channel-split-and-stage.md` argues
that early-stage content belongs on executive profiles and later-stage on the company page, and
that the argument holds **only under two conditions**: the company has a founder or executive
network it can actually use, and it is early enough that category demand has to be created rather
than captured. The intake asks about both. Until 12 Sep 2026 nothing read the answers.

So the split existed as a finding, and as a hand-applied convention, and never as something the
engine could recommend or refuse. A recipe rather than a rule, which is exactly what
`research/03` section 4 warns about.

**What this does NOT do.** It does not score slots and it does not reorder a calendar. It answers
one question, with reasons: given what this company actually said about itself, which channel
should carry which work, and are there conditions under which the usual answer is wrong here.

Ruling 4 still holds. It recommends; a person decides.
"""

from __future__ import annotations

from .scoring import JOB_SERVES, JOB_TO_TIER

# The three profile answers this reads, and what each one can be.
#
# Every value is something a person can answer from evidence rather than aspiration, which is the
# question-bank rule: `founder_network.viable` is meant to be set from *how many posts they have
# actually written*, not from whether they say they will.
VIABILITY = {"yes", "partial", "no"}
AWARENESS = {"unknown", "emerging", "established"}
EXPOSURE = {"low", "high"}

# WHICH JOBS EACH CHANNEL CARRIES. Derived from the tier, and **MOFU is deliberately on both.**
#
# A first version split this on whether a job serves creation more than capture, which put every
# MOFU job on the company page and left the executive channel TOFU-only. That contradicted the
# hypothesis this is built from, which was "TOFU and MOFU on the personal pages, MOFU and BOFU on
# the company page" *(Vatsal, 11 Sep 2026)*. **The overlap is the more careful position and the
# binary split threw it away.**
#
# The reason MOFU sits on both: requirements building serves a reader who is still working out
# what they need, and that reader can be discovering the category on a profile or already
# evaluating us on the page. Same job, same topic, different treatment. Which is the framework's
# own line, that a topic is not a funnel stage and the treatment is.
EARLY = [j for j, t in JOB_TO_TIER.items() if t in ("TOFU", "MOFU")]
LATE = [j for j, t in JOB_TO_TIER.items() if t in ("MOFU", "BOFU")]
SHARED = [j for j in EARLY if j in LATE]


def _tiers(jobs):
    return sorted({JOB_TO_TIER[j] for j in jobs}, key=["TOFU", "MOFU", "BOFU"].index)


def _yaml_word(v):
    """Turn YAML's booleans back into the words somebody typed.

    **YAML 1.1 reads `yes`, `no`, `on` and `off` as booleans**, so a profile saying
    `viable: yes` arrives here as `True` and fails a check expecting the string. The error then
    reads "viable is True, expected one of ['no', 'partial', 'yes']", which is both correct and
    baffling to the person who wrote the obvious thing.

    Quoting it in the file would fix one profile. Accepting it here fixes every profile anybody
    writes from now on, which is the difference between a tool and one person's tool.
    """
    if v is True:
        return "yes"
    if v is False:
        return "no"
    return v


def recommend_channels(profile: dict) -> dict:
    """Which channel carries which jobs, why, and when the usual answer does not apply.

    Returns `applies: False` when the conditions for an executive-led split are not met. **That
    is a real answer rather than a failure**, and it is the one the research section on "when the
    split does not apply" exists to produce.
    """
    strat = (profile or {}).get("channel_strategy") or {}
    out = {"applies": None, "reasons": [], "cautions": [], "channels": {}, "missing": []}

    network = _yaml_word((strat.get("founder_network") or {}).get("viable"))
    awareness = _yaml_word(strat.get("category_awareness"))
    exposure = _yaml_word(strat.get("named_person_exposure"))

    for name, val, allowed in (("founder_network.viable", network, VIABILITY),
                               ("category_awareness", awareness, AWARENESS),
                               ("named_person_exposure", exposure, EXPOSURE)):
        if val is None:
            out["missing"].append("%s not answered" % name)
        elif val not in allowed:
            out["missing"].append("%s is %r, expected one of %s" % (name, val, sorted(allowed)))

    if out["missing"]:
        out["reasons"].append(
            "cannot recommend a channel split: " + "; ".join(out["missing"])
            + ". These come from the intake, and guessing them is how a plan gets built on an "
              "input nobody agreed to supply")
        return out

    # --- condition 1, and it is the one that fails most often ------------------------------
    if network == "no":
        out["applies"] = False
        evidence = (strat.get("founder_network") or {}).get("evidence") or "no evidence recorded"
        out["reasons"].append(
            "No usable executive network, so an executive-led split does not apply. The company "
            "page is what you have. Evidence: %s" % evidence)
        out["channels"]["company"] = {
            "carries": sorted(set(EARLY) | set(LATE), key=list(JOB_TO_TIER).index),
            "tier_hint": "TOFU to BOFU",
            "why": "with no second channel the page carries the whole funnel, which it will do "
                   "badly at the top: a company page cannot win reach against a named profile",
        }
        out["cautions"].append(
            "Do not build a plan on executives posting. Stated intent is not evidence; the "
            "question that predicts this is how many originals they wrote in the last year")
        return out

    # --- condition 2: is there demand to capture, or must it be created? --------------------
    out["applies"] = True
    if awareness == "established":
        out["reasons"].append(
            "The buyer already knows the category exists, so capture is cheap and creation is "
            "less urgent. The usual split still holds but the weighting inverts: fund the "
            "company page first and treat the executive channel as reinforcement")
        primary = "company"
    else:
        out["reasons"].append(
            "Category awareness is %r, so few people are searching for something they do not "
            "know exists and capture catches almost nobody. Creation has to come first, and a "
            "named human is the cheapest creation channel available" % awareness)
        primary = "clevel"

    if network == "partial":
        out["cautions"].append(
            "Executive network is only partial, so the creation channel is the constraint rather "
            "than the plan. Size the calendar to what they have actually published before, not "
            "to what the channel could carry")

    out["reasons"].append(
        "MOFU sits on BOTH channels (%s). A reader working out what they need may be "
        "discovering the category on a profile or already evaluating us on the page: same job, "
        "different treatment" % ", ".join(SHARED))
    out["channels"]["clevel"] = {
        "carries": EARLY,
        "tier_hint": " to ".join(_tiers(EARLY)[:1] + _tiers(EARLY)[-1:]),
        "why": "a named profile reaches people who do not follow the company, which is the only "
               "way early-stage work finds anybody",
    }
    out["channels"]["company"] = {
        "carries": LATE,
        "tier_hint": " to ".join(_tiers(LATE)[:1] + _tiers(LATE)[-1:]),
        "why": "a visitor to the page has already arrived, so the page is a validation surface "
               "rather than a reach surface",
    }
    out["primary"] = primary

    # --- the condition that moves claim-bearing work back to the page ----------------------
    if exposure == "high":
        out["cautions"].append(
            "A named person making a claim here carries personal or regulatory exposure, so "
            "claim-bearing content belongs on the company page even where the split would "
            "otherwise put it on a profile. Split by WHO CARRIES THE RISK, not only by stage")
        out["channels"]["clevel"]["why"] += ", but it carries mechanism and judgement rather " \
                                            "than claims"
    return out


def describe(rec: dict) -> str:
    """One readable block. The reasoning is the product, so it has to be printable."""
    lines = []
    if rec["applies"] is None:
        lines.append("NO RECOMMENDATION")
    elif rec["applies"]:
        lines.append("Executive-led split APPLIES. Primary channel: %s" % rec.get("primary"))
    else:
        lines.append("Executive-led split DOES NOT APPLY")
    for r in rec["reasons"]:
        lines.append("  because: %s" % r)
    for ch, d in rec["channels"].items():
        lines.append("  %-8s %s  (%s)" % (ch, ", ".join(d["carries"]), d["tier_hint"]))
        lines.append("           %s" % d["why"])
    for c in rec["cautions"]:
        lines.append("  CAUTION: %s" % c)
    return "\n".join(lines)
