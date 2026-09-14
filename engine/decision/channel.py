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

from .company_type import implications
from .scoring import JOB_SERVES, JOB_TO_TIER

# The three profile answers this reads, and what each one can be.
#
# Every value is something a person can answer from evidence rather than aspiration, which is the
# question-bank rule: `founder_network.viable` is meant to be set from *how many posts they have
# actually written*, not from whether they say they will.
VIABILITY = {"yes", "partial", "no"}
AWARENESS = {"unknown", "emerging", "established"}
EXPOSURE = {"low", "high"}

# THE TWO KINDS OF CHANNEL, AND ONLY TWO. A profile names its own channels and says which kind
# each one is; the engine never assumes how many there are or what they are called.
#
# Why two kinds rather than a free-for-all: the distinction is structural, not cosmetic. A named
# person reaches people who do not follow the company, and an organisation page is read by
# somebody who has already arrived. Every asymmetry in this module follows from that one fact,
# and no third kind has turned up that behaves differently from one of these two.
#
#   person        a named human's own feed. Carries creation work
#   organisation  a company page, brand account or publication. Carries capture work
KINDS = {"person", "organisation"}

# ==================================================================================================
# WHICH SEAT A PERSON CHANNEL SITS IN. Optional, and the most consequential optional thing in a
# profile: measured against the company's own page in the same window (`docs/BENCHMARKS.md`), a
# founder's median post ran 3.06x the page's and won 19 of 23 pairs, while a VP's ran 0.54x and won
# 1 of 4. The gap between two person channels is larger than the gap between a person and a page,
# which means "get the executives posting" is not a strategy and "get the founder posting" is.
#
# The seat also predicts what the channel can carry. A founder's published mix is close to
# identical to their own page's (28/11/10/44 against 31/10/12/45 on TOFU/MOFU/BOFU/non-buying).
# Below that seat the funnel collapses: individual contributors measured 1% BOFU and 4% MOFU.
#
# Carried as expectations and cautions. No multipliers: these describe 39 paired accounts in one
# window, and a description of somebody else's audience is not a coefficient.
# ==================================================================================================
SEATS = {
    "founder": {
        "ratio": "3.06x the company page's median, winning 19 of 23 measured pairs",
        "carries": "the same mix the page carries, and it is the only seat measured that does",
        "caution": None,
    },
    "c-suite": {
        "ratio": "1.91x, on only 3 measured pairs",
        "carries": "the most TOFU-heavy mix measured, though on a small sample",
        "caution": "**the C-suite reading rests on 3 pairs and 60 posts.** Treat it as a lead to "
                   "check against your own corpus rather than a number to plan against",
    },
    "vp": {
        "ratio": "0.54x, winning 1 of 4 measured pairs",
        "carries": "4% MOFU and 5% BOFU: mostly non-buying content",
        "caution": "**this seat underperformed the company page in the measured sample.** That is "
                   "four people and not a verdict, but it is the one seat where the usual advice "
                   "to amplify executives pointed the wrong way. Measure this pair before "
                   "planning around it",
    },
    "ic": {
        "ratio": "1.03x: level with the page",
        "carries": "1% BOFU and 4% MOFU against 58% non-buying",
        "caution": "**an individual contributor's channel is a personal brand, which is a real "
                   "thing and is not a sales channel.** Expect reach and community, not "
                   "evaluation content, and do not plan BOFU onto it",
    },
}

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

    # WHICH CHANNELS EXIST IS THE PROFILE'S TO SAY, not this module's to assume. It used to
    # hardcode exactly two, called `clevel` and `company`, so a company with three named people
    # or only a page could not describe itself.
    declared = (profile or {}).get("channels") or {}
    if not declared:
        out["missing"].append(
            "no `channels:` declared. Name each channel and say whether its kind is `person` or "
            "`organisation`. There is no sensible default: how many channels exist, and who "
            "they belong to, is a fact about the company rather than about the engine")
    for name, spec in declared.items():
        kind = (spec or {}).get("kind")
        seat = str((spec or {}).get("seat") or "").strip().lower()
        if kind == "person":
            if seat in SEATS:
                s = SEATS[seat]
                out["reasons"].append(
                    "%s is a `%s` seat. Comparable channels ran %s, and carry %s"
                    % (name, seat, s["ratio"], s["carries"]))
                if s["caution"]:
                    out["cautions"].append("%s: %s" % (name, s["caution"]))
            elif seat:
                out["cautions"].append(
                    "channel %r has seat %r, which is not one of %s -- it is being ignored, and a "
                    "typo here fails silently" % (name, seat, sorted(SEATS)))
            else:
                out["cautions"].append(
                    "channel %r is a person but declares no `seat`. Which seat it is moves "
                    "outcomes more than person-versus-page does: a founder ran 3.06x their own "
                    "page and a VP ran 0.54x. Declaring it costs one line" % name)
        if kind not in KINDS:
            out["missing"].append(
                "channel %r has kind %r, expected `person` or `organisation`" % (name, kind))

    if out["missing"]:
        out["reasons"].append(
            "cannot recommend a channel split: " + "; ".join(out["missing"])
            + ". These come from the intake, and guessing them is how a plan gets built on an "
              "input nobody agreed to supply")
        return out

    people = [n for n, d in declared.items() if d["kind"] == "person"]
    orgs = [n for n, d in declared.items() if d["kind"] == "organisation"]

    everything = sorted(set(EARLY) | set(LATE), key=list(JOB_TO_TIER).index)

    # --- condition 1: is there a usable named channel at all? ------------------------------
    #
    # Two separate ways this fails, and they are worth telling apart. A profile can declare no
    # person channel, meaning one does not exist. Or it can declare one while the intake says
    # the person will not actually post, which is the more common and more expensive case.
    if not people or network == "no":
        out["applies"] = False
        if not people:
            out["reasons"].append(
                "No channel of kind `person` is declared, so there is no creation channel. "
                "Everything falls to the organisation channel")
        else:
            evidence = (strat.get("founder_network") or {}).get("evidence") or "none recorded"
            out["reasons"].append(
                "A person channel exists (%s) but the intake says the network is not usable, so "
                "an executive-led split does not apply. Evidence: %s"
                % (", ".join(people), evidence))
            out["cautions"].append(
                "Do not build a plan on a named person posting. Stated intent is not evidence; "
                "the question that predicts it is how many originals they wrote last year")
        if not orgs:
            out["cautions"].append(
                "**And no organisation channel is declared either, so nothing carries anything.** "
                "Declare at least one channel this company can actually publish on")
        for name in orgs:
            out["channels"][name] = {
                "kind": "organisation", "carries": everything, "tier_hint": "TOFU to BOFU",
                "why": "with no usable named channel this page carries the whole funnel, which "
                       "it will do badly at the top: a page cannot win reach against a person",
            }
        return out

    # --- condition 2: is there demand to capture, or must it be created? --------------------
    out["applies"] = True
    if awareness == "established":
        out["reasons"].append(
            "The buyer already knows the category exists, so capture is cheap and creation is "
            "less urgent. The usual split still holds but the weighting inverts: fund the "
            "company page first and treat the executive channel as reinforcement")
        primary = orgs[0] if orgs else people[0]
    else:
        out["reasons"].append(
            "Category awareness is %r, so few people are searching for something they do not "
            "know exists and capture catches almost nobody. Creation has to come first, and a "
            "named human is the cheapest creation channel available" % awareness)
        primary = people[0]

    if network == "partial":
        out["cautions"].append(
            "Executive network is only partial, so the creation channel is the constraint rather "
            "than the plan. Size the calendar to what they have actually published before, not "
            "to what the channel could carry")

    out["reasons"].append(
        "MOFU sits on BOTH channels (%s). A reader working out what they need may be "
        "discovering the category on a profile or already evaluating us on the page: same job, "
        "different treatment" % ", ".join(SHARED))
    for name in people:
        out["channels"][name] = {
            "kind": "person",
            "carries": EARLY,
            "tier_hint": " to ".join(_tiers(EARLY)[:1] + _tiers(EARLY)[-1:]),
            "why": "a named profile reaches people who do not follow the company, which is the "
                   "only way early-stage work finds anybody",
        }
    for name in orgs:
        out["channels"][name] = {
            "kind": "organisation",
            "carries": LATE,
            "tier_hint": " to ".join(_tiers(LATE)[:1] + _tiers(LATE)[-1:]),
            "why": "a visitor to the page has already arrived, so the page is a validation "
                   "surface rather than a reach surface",
        }

    # **Two named people get the same job set, and that is the finding rather than a shortcut.**
    # Asked separately what their channels were for, two executives at one company returned
    # identical answers. What actually separated them was mode: one spoke at events, the other
    # wrote articles. A mode difference sets format and source material, not which buying jobs
    # the channel does, so it belongs in each channel's own notes rather than in this split.
    if len(people) > 1:
        out["cautions"].append(
            "%d person channels carry the same jobs. What separates them is MODE — who speaks "
            "at events, who writes long form, who has photographs — which sets format and source "
            "material rather than which jobs they do. Record that per channel; do not expect "
            "this split to distinguish them" % len(people))
    if not orgs:
        out["cautions"].append(
            "No organisation channel is declared, so validation and consensus work has nowhere "
            "to go. Those are the jobs a buyer close to deciding needs")
    # WHAT YOU SELL CAN OVERRIDE WHAT THE MARKET KNOWS. Awareness decides which channel gets
    # funded first for most companies; for a service it does not get to, because the thing being
    # bought is the people. An organisation page cannot answer "do I want these specific humans
    # in my business", and that is the question a service buyer is actually asking.
    imp = implications(profile)
    if imp["declared"] and imp["offering"] == "service" and people and primary not in people:
        out["reasons"].append(
            "OVERRIDDEN by what this company sells. Awareness would have funded the page first, "
            "but a service sale is a bet on people and the content that works has a person's "
            "name on it. %s is the primary channel here regardless of awareness" % people[0])
        primary = people[0]
    for c in imp["cautions"]:
        out["cautions"].append(c)
    if not imp["declared"]:
        out["cautions"].append(
            "company_type is not declared, so nothing about what you sell or how it is bought "
            "shaped this. That is a real gap: most content advice assumes SaaS sold PLG and "
            "transfers badly to anything else")

    out["primary"] = primary

    # --- the condition that moves claim-bearing work back to the page ----------------------
    if exposure == "high":
        out["cautions"].append(
            "A named person making a claim here carries personal or regulatory exposure, so "
            "claim-bearing content belongs on the company page even where the split would "
            "otherwise put it on a profile. Split by WHO CARRIES THE RISK, not only by stage")
        for name in people:
            out["channels"][name]["why"] += (", but it carries mechanism and judgement rather "
                                             "than claims")
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
