#!/usr/bin/env python3
"""Score a content slot: Gate, Lift, and as much of Fit as the profile supports.

Three outputs, never averaged into one, because they fail differently and the fix differs.

  Gate   may we publish this at all          binary, runs first
  Lift   what is this treatment worth        measured from the company's own corpus
  Fit    is this the right thing to say      needs objective weights; returns None without them

**Every number arrives with its components.** Ruling 4 puts a human in the decision, so the
reasoning is the product. A score nobody can argue with is not useful to a person who has to decide.

**Fit returns None rather than a default when weights are missing.** A plausible-looking number
computed from nothing is worse than an honest gap, and the gap is the thing that tells you the
elicitation has not been run.

Measured constants carry their provenance inline. Anything not measured is marked and excluded
from the score rather than guessed.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------------------------
# THIS MODULE CARRIES NO MEASUREMENTS. That is the design, not an omission.
#
# An earlier version shipped one company's length bands, format medians and competitor counts as
# a fallback, so any company that had not measured its own corpus still got a score. The score
# looked exactly like a real one. **A number computed from somebody else's audience is not wrong
# so much as meaningless**, and nothing in the output said which it was.
#
# Every measurement now comes from the profile of the company being written for. Without one,
# Lift and Fit return `None` and name the input that is missing. See `profiles/_schema.md` for
# the shape and `profiles/example-meridian.md` for a filled-in one.
#
# **Refusing is the useful behaviour.** The gap is what tells you the corpus has never been
# measured, and that is a real finding about the project rather than a defect in the tool.
# ---------------------------------------------------------------------------------------------

# WHAT EACH FORMAT COSTS TO PRODUCE. **Not a measurement, so it stays.**
#
# Lift can rank formats from a corpus. It cannot know whether anybody can make one. A photo
# album is three phone photographs; a designed carousel is a designer. `recommend()` returns the
# precondition alongside every option so the person who knows the answer can give it.
#
# This is why the cheap format is often nearly the best one, and why a format nobody has time to
# produce is worth nothing however well it scores.
FORMAT_REQUIREMENT = {
    "photo album": "3 to 5 photographs exist, or can be taken on a phone",
    "single image": "1 photograph exists",
    "text": "nothing",
    "carousel": "design time, and consistent aspect ratios across every card",
    "video": "shooting and editing time",
}

# Proof tiers the calendar already uses, ordered by how much weight they carry with a buyer who
# is checking. Mirrors the existing PROOF dict in gen_content_calendar.py rather than inventing
# a second vocabulary.
PROOF_WEIGHT = {"MEASURED": 1.0, "SPEC": 0.8, "MODELLED": 0.5, "NONE": 0.3}

# Buying jobs, from the primary research rather than the funnel folklore. The funnel label is
# derived from the job, per ruling 2: classify by job, label by funnel.
JOB_TO_TIER = {
    "problem identification": "TOFU",
    "solution exploration": "TOFU",
    "requirements building": "MOFU",
    "supplier selection": "MOFU",
    "validation": "BOFU",
    "consensus creation": "BOFU",
}

# ---------------------------------------------------------------------------------------------
# WHAT EACH BUYING JOB SERVES. **Added 11 Sep 2026**, when the first profile brought real weights.
#
# The engine knows two kinds of objective and no more: **capture** moves a buyer who has already
# identified themselves, **create** builds standing among people who are not in market yet. A
# profile declares which kind each of its own objectives is; the engine never has to know what a
# "qualified plant conversation" means.
#
# This table is INFERRED, like the angle mapping, and for the same reason it is written down
# rather than buried: it is arguable and it should be argued with. The shape is not controversial
# (early jobs reach strangers, late jobs serve people already looking) but the numbers are a
# judgement.
#
# **Channel is deliberately NOT a second component.** The company page is already almost entirely
# late-stage jobs and the executive feeds almost entirely early ones, so scoring channel as well
# would count the same fact twice and make the split look stronger than the evidence for it.
JOB_SERVES = {
    "problem identification": {"create": 1.0, "capture": 0.2},
    "solution exploration":   {"create": 0.8, "capture": 0.4},
    "requirements building":  {"create": 0.4, "capture": 0.8},
    "supplier selection":     {"create": 0.3, "capture": 0.9},
    "validation":             {"create": 0.1, "capture": 1.0},
    "consensus creation":     {"create": 0.0, "capture": 1.0},
}

# ---------------------------------------------------------------------------------------------
# ANGLE TO BUYING JOB. **Extended 11 Sep 2026**, from 15 angles to 26, after the first backtest
# left 12 of 36 slots unclassified: 8 of 12 company-page angles had no mapping at all.
#
# The mapping is still INFERRED rather than measured, and it is still the weakest link in the
# scorer. What changed is that it now applies one written test instead of intuition per angle:
#
#     WHAT CAN THE READER DO NEXT THAT THEY COULD NOT DO BEFORE?
#
#       counts a cost they were not counting          -> problem identification
#       knows what kinds of answer exist              -> solution exploration
#       can size or specify what they need            -> requirements building
#       can tell two vendors apart                    -> supplier selection
#       can be sure a provisional choice will hold    -> validation
#       can defend the choice to somebody who was not
#         in the room, with no seller present         -> consensus creation
#
# A SECOND TEST settles the cases the first one leaves ambiguous:
#
#     IS THE EVIDENCE VENDOR-SPECIFIC?
#
# A mechanism any competent machine could perform is exploration or requirements. A number, a
# model name or a site that only we can produce is **validation**, because its only function is
# to make one candidate credible. This is what separates slot 3 (dispatch mechanism, no product
# named, no figure) from a product-in-action post naming a model and quoting its spec. Under the
# first test alone both looked like category education, and only one of them is.
#
# The test is written down so a disagreement is about the test rather than about taste. Where a
# slot's angle is too coarse to carry its job, **the slot declares `job=` and that wins.** The
# angle is a treatment; the job is an intent; one does not reliably imply the other.
# ---------------------------------------------------------------------------------------------
ANGLE_TO_JOB = {
    # --- problem identification: the reader learns they have a problem ------------------------
    "problem-reframe": "problem identification",
    "industry-reflection": "problem identification",
    "cost-of-inaction": "problem identification",      # a wage line nobody was counting

    # --- solution exploration: the reader learns what kinds of answer exist -------------------
    "definitional": "solution exploration",            # CHANGED 11 Sep from problem
                                                       # identification. A definition that names
                                                       # where the answer is no tells you which
                                                       # category applies. Same tier either way
    "explainer": "solution exploration",
    "category-education": "solution exploration",
    "field-observation": "solution exploration",
    "how-it-works": "solution exploration",            # mechanism, no product named
    "failure-and-lesson": "solution exploration",      # teaches a category pitfall, not a track
                                                       # record. Names no customer and carries no
                                                       # proof, by its own brief

    # --- requirements building: the reader can size or specify -------------------------------
    "sizing": "requirements building",
    "comparison": "requirements building",
    "myth-correction": "requirements building",        # every instance so far is a sizing myth
    "safety-mechanism": "requirements building",       # an EHS reader setting what is acceptable
    "cost-model": "requirements building",             # shape of the curve, for a business case
    "contrarian": "requirements building",             # "when not to" is a qualification test and
                                                       # presupposes the reader is considering it

    # --- supplier selection: the reader can tell vendors apart -------------------------------
    "milestone": "supplier selection",                 # the credibility tile. Is this vendor real
                                                       # enough to put on a shortlist

    # --- validation: the reader can be sure a provisional choice holds -----------------------
    "measured-scale": "validation",
    "capability-proof": "validation",
    "case-evidence": "validation",
    "in-motion": "validation",                         # REVISED 11 Sep, was solution
                                                       # exploration. Product in action names a
                                                       # model and carries a spec claim, so it
                                                       # is vendor-specific evidence and cannot
                                                       # be category education. Second test
    "single-vehicle": "validation",                    # the per-vehicle odometer a maintenance
                                                       # lead asks for before signing
    "how-it-rolled-out": "validation",                 # will it land without stopping production
    "what-we-build": "validation",                     # who fixes this in year four
    "readiness-check": "validation",                   # AMBIGUOUS, and recorded as such. Sits
                                                       # between requirements and validation.
                                                       # Called validation because the reader is
                                                       # checking a decision already provisional

    # --- consensus creation: defensible to somebody who was not in the room ------------------
    "objection-handling": "consensus creation",
    "change-scenario": "consensus creation",           # "what if the layout changes" is asked by
                                                       # the person who was not in the meeting
}

# Angles that serve a REAL objective which is not a buying job. **Added 11 Sep 2026.**
#
# The first backtest reported four slots as "serves no buying job", which was true and useless.
# Naming the objective instead turns a null into an input: if content is being spent on an
# objective nobody weighted, that is either a gap in the weights or slots that should be cut,
# and the elicitation is where it gets settled. Reputation is a stated objective at most
# companies, so authority content is rarely unweighted on purpose.
ANGLE_TO_OTHER_OBJECTIVE = {
    "hiring": "recruitment",
    "career-arc": "authority",
}


def corpus(profile: dict | None = None) -> dict:
    """Whatever this company has measured. **Missing is a valid and common answer.**

    Returns each component or `None`, never a substitute. A caller that gets `None` must decline
    to score that component and say so; there is nothing here to fall back to on purpose.
    """
    c = ((profile or {}).get("corpus") or {})
    bands = c.get("length_bands")
    fmt = c.get("format_lift") or {}
    return {
        "length_bands": [tuple(b) for b in bands] if bands else None,
        "format_lift": {"clevel": fmt.get("clevel"), "company": fmt.get("company")},
        "saturation": c.get("saturation") or None,
        "measured": sorted(k for k in ("length_bands", "format_lift", "saturation")
                           if (c.get(k) if k != "format_lift" else fmt)),
    }


def _band_lift(words: int, bands) -> tuple[float, str]:
    for lo, hi, val in bands:
        if lo <= words <= hi:
            return val, f"{words}w sits in the {lo} to {hi} band, median {val}"
    lowest = min(b[2] for b in bands)
    return lowest, f"{words}w is below every measured band, scored at the lowest one"


def gate(slot: dict) -> dict:
    """Binary. Runs first. Reuses the calendar's own proof/source discipline."""
    reasons = []
    proof = slot.get("proof", "NONE")
    if proof not in PROOF_WEIGHT:
        reasons.append(f"unknown proof tier {proof!r}")
    if proof in ("MEASURED", "SPEC", "MODELLED") and not slot.get("source"):
        reasons.append(f"proof tier {proof} with no source named")
    if slot.get("fmt") == "video":
        reasons.append("video is out on production bandwidth")
    if slot.get("fmt") == "carousel" and slot.get("who"):
        reasons.append("designed carousel on an executive profile is out on design bandwidth")
    return {"pass": not reasons, "reasons": reasons}


def lift(slot: dict, channel: str = "clevel", profile: dict | None = None) -> dict:
    """What this treatment is worth, from the measured corpus. Normalised so 1.0 is the best
    measured option on each component, which keeps the components readable next to each other."""
    comps, notes = {}, []
    corp = corpus(profile)
    bands = corp["length_bands"]

    words = slot.get("words")
    if not bands:
        notes.append("no length bands in the profile, so length is not scored. Measure your own "
                     "corpus: median engagement by word count, on your own channel")
    elif words:
        raw, why = _band_lift(words, bands)
        comps["length"] = round(raw / max(b[2] for b in bands), 3)
        notes.append(why)
    else:
        notes.append("no word target set, length not scored")

    fmt = slot.get("fmt")
    table = corp["format_lift"].get(channel)
    if not table:
        notes.append(f"format lift is UNMEASURED for the {channel} channel, excluded from the "
                     f"score. One channel's medians never transfer to another")
    elif fmt in table:
        comps["format"] = round(table[fmt] / max(table.values()), 3)
        notes.append(f"{fmt} medians {table[fmt]} for this market")
    elif fmt:
        notes.append(f"format {fmt!r} not in the measured table, excluded")

    score = round(sum(comps.values()) / len(comps), 3) if comps else None
    return {"score": score, "components": comps, "notes": notes}


def classify(slot: dict) -> dict:
    """Buying job first, funnel label derived from it. Ruling 2.

    Precedence: a `job` declared on the slot wins over the angle mapping, because the angle is a
    treatment and the job is an intent. `source` records which one answered, so a tier derived
    from a coarse default is never mistaken for one a person set.
    """
    angle = slot.get("angle")

    declared = slot.get("job")
    if declared:
        if declared not in JOB_TO_TIER:
            return {"job": None, "label": None, "derived": False, "source": "declared",
                    "objective": None,
                    "note": "slot declares job %r, which is not one of the six" % declared}
        return {"job": declared, "label": JOB_TO_TIER[declared], "derived": True,
                "source": "declared", "objective": None,
                "note": "slot declares the %s job, overriding angle %r" % (declared, angle)}

    other = ANGLE_TO_OTHER_OBJECTIVE.get(angle)
    if other:
        return {"job": None, "label": None, "derived": True, "source": "angle",
                "objective": other,
                "note": "angle %r serves %s, which is an objective and not a buying job. "
                        "It needs a weight or the slot needs cutting" % (angle, other)}

    job = ANGLE_TO_JOB.get(angle, "UNMAPPED")
    if job == "UNMAPPED":
        return {"job": None, "label": None, "derived": False, "source": "angle",
                "objective": None,
                "note": "angle %r has no job mapping. Add one or the tier stays a guess" % angle}
    return {"job": job, "label": JOB_TO_TIER[job], "derived": True, "source": "angle",
            "objective": None,
            "note": "angle %r does the %s job" % (angle, job)}


def fit(slot: dict, profile: dict, cls: dict | None = None) -> dict:
    """Is this the right thing to say, for what this company is trying to do.

    Three components, and they do not fail the same way, so they are not treated the same way:

      alignment   does the buying job this slot does serve the objectives that carry the weight.
                  **Load-bearing. Without it there is no score**, because this is the component
                  the whole framework exists to compute
      openness    is the theme crowded. Degrades gracefully: on a real calendar a third or more
                  of slots sit outside every measured theme, and withholding them all is worse
                  than reporting one built on fewer parts and saying so
      proof       what tier of evidence is available

    `basis` names the components that actually went in, so a ranking script can refuse to compare
    a three-component score against a two-component one without noticing.

    **The components are averaged with equal weight, and that is a choice rather than a finding.**
    Nothing has been measured about how much openness should count against proof availability, so
    any other split would be invented. Equal weighting is the only one that claims no knowledge.
    It is recorded here because an unexamined default inside a scorer is how an assumption becomes
    a fact. **What would settle it:** published outcomes tagged with their components, enough of
    them to regress engagement or conversation against each. Nobody has that yet.
    """
    comps, missing, notes, by_kind = {}, [], [], {}
    cls = cls if cls is not None else classify(slot)

    # --- alignment, the load-bearing one -------------------------------------------------
    kinds = _weights_by_kind(profile)
    if not kinds:
        missing.append("objective weights not elicited, so objective alignment is not scored")
    elif cls.get("objective"):
        return {"score": None, "components": {}, "basis": [], "by_kind": {},
                "missing": ["funded outside the ranked budget"],
                "notes": ["serves %s, which this profile funds on a separate budget. Scored "
                          "against its own quota, never ranked against the 100 points"
                          % cls["objective"]]}
    elif not cls.get("job"):
        missing.append("no buying job, so there is nothing to align to the objectives")
    else:
        served = JOB_SERVES[cls["job"]]
        comps["alignment"] = round(sum(kinds[k] * served[k] for k in kinds), 3)
        # **Kept separate as well as blended, and this is not decoration.** Objectives commonly
        # sit on different clocks: one quarter against three years. Step 3 of the elicitation
        # warns that a long-horizon objective always loses a blended allocation, because this
        # quarter is vivid and three years away is abstract. A single Fit number ranks a
        # reputation slot against a pipeline slot and the slow one loses every time, which is
        # how a company arrives in two years wondering why it is known for nothing. So the
        # per-objective value is reported too, and a ranking can be run inside one clock.
        by_kind = {k: round(served[k], 3) for k in kinds}
        lead = max(kinds, key=kinds.get)
        notes.append("the %s job serves %s at %s, against %s weight on %s objectives"
                     % (cls["job"], lead, served[lead], round(kinds[lead], 2), lead))

    # --- openness, which degrades rather than blocks --------------------------------------
    sat = corpus(profile)["saturation"] or {}
    theme = slot.get("theme")
    if theme and theme in sat:
        n, ceiling = sat[theme], max(sat.values())
        comps["openness"] = round(1.0 - min(n, ceiling) / ceiling, 3)
        notes.append("%s holds %s competitor chunks" % (theme, n))
    else:
        missing.append("theme %r is in no measured saturation bucket, openness not scored"
                       % (theme or None))

    comps["proof"] = PROOF_WEIGHT.get(slot.get("proof", "NONE"), 0.3)
    notes.append("proof tier %s" % slot.get("proof", "NONE"))

    if "alignment" not in comps:
        return {"score": None, "components": comps, "basis": [], "missing": missing,
                "by_kind": {},
                "notes": notes + ["score withheld: alignment is the load-bearing component"]}
    score = round(sum(comps.values()) / len(comps), 3)
    return {"score": score, "components": comps, "basis": sorted(comps), "missing": missing,
            "by_kind": by_kind, "notes": notes}


def _weights_by_kind(profile: dict) -> dict:
    """Read the profile's objective weights, collapsed to the two kinds the engine knows.

    Accepts either a loaded profile dict or a pre-collapsed mapping, so a caller can score
    against a hypothetical split without writing a profile file for it.
    """
    if not profile:
        return {}
    obj = profile.get("objectives") or {}
    weights, kinds = obj.get("weights") or {}, obj.get("kinds") or {}
    if weights and kinds:
        out = {"capture": 0.0, "create": 0.0}
        for name, w in weights.items():
            k = kinds.get(name)
            if k in out:
                out[k] += w / 100.0
        return out
    direct = profile.get("weights_by_kind")
    return dict(direct) if direct else {}


def recommend(slot: dict, channel: str = "clevel", profile: dict | None = None) -> dict:
    """What Lift would set for format and length, and what it refuses to set.

    **Gate runs before Lift, in that order.** Recommending a format the claim and bandwidth
    rules have banned would be a scorer arguing with a ruling, so blocked formats are removed
    from the ranking rather than ranked and ignored.

    Two honest limits, both reported rather than papered over:

    - **Lift ranks formats. It cannot know whether the raw material exists.** So every option
      carries its production precondition and the human answers that.
    - **Lift picks a length BAND, not a number.** The best measured band is 180 words and above
      and the corpus does not resolve inside it: 230 and 340 are indistinguishable to it. So a
      word target can be validated against the band and cannot be derived from it. A scorer that
      emitted "use 283 words" would be inventing precision the measurement does not carry.
    """
    corp = corpus(profile)
    table = corp["format_lift"].get(channel)
    out = {"format": None, "options": [], "words": None, "notes": []}

    if not table:
        out["notes"].append(
            "format lift is UNMEASURED for the %s channel, so no format is recommended. "
            "Competitor page data exists but it is another company's audience." % channel)
    else:
        current = slot.get("fmt")
        survivors = []
        for fmt, median in sorted(table.items(), key=lambda kv: -kv[1]):
            probe = dict(slot)
            probe["fmt"] = fmt
            g = gate(probe)
            if not g["pass"]:
                out["notes"].append("%s excluded: %s" % (fmt, "; ".join(g["reasons"])))
                continue
            survivors.append((fmt, median))
        base = table.get(current)
        for fmt, median in survivors:
            out["options"].append({
                "fmt": fmt,
                "median": median,
                "vs_current": round(median / base, 2) if base else None,
                "needs": FORMAT_REQUIREMENT.get(fmt, "unknown"),
            })
        if survivors:
            out["format"] = survivors[0][0]
            if current == out["format"]:
                out["notes"].append("already on the best surviving format")
            elif base:
                out["notes"].append(
                    "%s medians %s against %s for %s, a %sx difference, and it needs: %s"
                    % (out["format"], survivors[0][1], base, current,
                       round(survivors[0][1] / base, 2), FORMAT_REQUIREMENT[out["format"]]))

    words = slot.get("words")
    if not corp["length_bands"]:
        out["words"] = {"floor": None, "in_best_band": None,
                        "note": "no length bands in the profile, so no word target can be "
                                "recommended. This is measurable in an afternoon from your own "
                                "published posts and it is the single biggest lever on most "
                                "channels"}
        return out
    best_lo, _, best_median = corp["length_bands"][0]
    if words is None:
        out["words"] = {"floor": best_lo, "in_best_band": None,
                        "note": "no word target set on this slot. The best measured band is "
                                "%d+ at a %s median" % (best_lo, best_median)}
    else:
        in_best = words >= best_lo
        out["words"] = {"floor": best_lo, "in_best_band": in_best,
                        "note": ("%dw is in the best measured band (%d+). Lift confirms the "
                                 "target and cannot improve on it: the band is open-ended and "
                                 "the corpus does not resolve inside it"
                                 % (words, best_lo)) if in_best else
                                ("%dw is BELOW the best band. Moving it to %d+ is worth %sx on "
                                 "the measured medians"
                                 % (words, best_lo,
                                    round(best_median / _band_lift(words, corp["length_bands"])[0],
                                          2)))}
    return out


def score_slot(slot: dict, profile: dict | None = None, channel: str = "clevel") -> dict:
    g, l, c = gate(slot), lift(slot, channel, profile), classify(slot)
    f = fit(slot, profile or {}, cls=c)      # one classification, so the two cannot disagree
    if not g["pass"]:
        why = "BLOCKED: " + "; ".join(g["reasons"])
    elif f["score"] is None:
        why = (f"Lift {l['score']}, Fit withheld ({'; '.join(f['missing'])})")
    else:
        why = f"Lift {l['score']}, Fit {f['score']}"
    return {"n": slot.get("n"), "gate": g, "lift": l, "fit": f, "tier": c, "why": why}
