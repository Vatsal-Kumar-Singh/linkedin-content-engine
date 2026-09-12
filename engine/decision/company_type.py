#!/usr/bin/env python3
"""What a company's type changes about the answer.

**Two independent axes**: what you sell, and how it gets bought. A SaaS product can be PLG or
SLG; a service is almost never PLG. Treating them as one axis is the error that makes most
published advice untransferable, and `docs/decision/RESEARCH-company-type.md` is the long version.

Until this module existed, `company_type` sat in the profile and **nothing read it.** It was a
note, not a decision. This makes it one.

---

**It returns constraints and cautions, never score multipliers.** That is deliberate. The
research says which jobs are load-bearing for which buying model; it does not say by how much,
and nobody has measured it. A scorer that refuses to invent a length band should not quietly
invent a 1.4x on consensus content because a document implied it mattered.

So the shape of what comes back is: *these jobs carry the deal for you, these ones barely apply,
and here is the reason* — which a person can act on and argue with, and which a calendar check
can enforce without pretending to a precision nobody has.
"""

from __future__ import annotations

OFFERING = {"saas", "service", "product"}
MOTION = {"plg", "slg", "pls", "enterprise"}

# --- Axis 2: how it gets bought ---------------------------------------------------------------
#
# The single most useful distinction in the whole framework: **in PLG the reader IS the buyer; in
# SLG the reader is often a messenger.** SLG content has a second audience it never meets, which
# is the rest of the committee, and that changes the artefact — it has to survive being forwarded
# with nobody there to explain it.
MOTION_RULES = {
    "plg": {
        "load_bearing": ["solution exploration", "requirements building"],
        "discounted": ["consensus creation"],
        "why_discounted": "one user decides, so there is no committee to build consensus in. "
                          "Consensus content here is answering an objection nobody is raising",
        "artefact": "the reader is the buyer, so content can assume the person reading it is the "
                    "person acting. It does not have to survive being forwarded",
    },
    "slg": {
        "load_bearing": ["consensus creation", "supplier selection", "validation"],
        "discounted": [],
        "why_discounted": "",
        "artefact": "**the reader is often a messenger.** There is a second audience you never "
                    "meet, and the artefact has to survive being forwarded without you in the "
                    "room. A case study that only makes sense with a salesperson explaining it "
                    "has failed at its actual job",
    },
    "pls": {
        "load_bearing": ["solution exploration", "consensus creation"],
        "discounted": [],
        "why_discounted": "",
        "artefact": "both readers exist at different moments: a user who acts alone first, then "
                    "a committee. The same library has to serve each without either feeling "
                    "written for the other",
    },
    "enterprise": {
        "load_bearing": ["consensus creation", "validation", "supplier selection"],
        "discounted": ["problem identification"],
        "why_discounted": "a committee with a budget cycle already knows it has the problem. "
                          "What it needs is to survive procurement and engineering review",
        "artefact": "it will be forwarded internally, frequently as a PDF, and read by people "
                    "who will never contact you",
    },
}

# --- Axis 1: what you sell ---------------------------------------------------------------------
OFFERING_RULES = {
    "saas": {
        "proof": "trial, usage, integrations",
        "blockers": "IT, security, procurement",
        "channel": None,
        "gate": "claims are mostly about behaviour and are correctable. The Gate still matters "
                "and it is not a regulatory question",
    },
    "service": {
        "proof": "named people, prior work, visible process",
        "blockers": "nobody formally. Trust fails quietly and you are not told",
        # The finding worth the whole document.
        "channel": "**A service sale is a bet on people, so the content that works has a "
                   "person's name on it.** Founder and executive content is not one tactic among "
                   "several here, it is the primary channel, and an organisation page carrying "
                   "the weight is a strategy working against the thing being bought",
        "gate": "the claims are about capability and outcomes. Overstating is a trust failure "
                "rather than a compliance one, and it is invisible until the deal quietly dies",
    },
    "product": {
        "proof": "deployments, specifications, certifications",
        "blockers": "engineering, safety, finance",
        "channel": None,
        "gate": "**claims are checkable and wrong ones are expensive.** A capability claim can "
                "be tested on site and a certification claim is a regulatory exposure rather "
                "than a marketing overreach. This is why the Gate is a hard binary rather than "
                "a style guideline",
    },
}


def implications(profile: dict) -> dict:
    """What this company's type means for the calendar. Refuses rather than assuming a default.

    **An undeclared type is not a SaaS PLG company.** Most published content advice is written
    for that case and reads plausible everywhere because the vocabulary is generic, which is the
    most common reason a content strategy underperforms with nobody able to say why. So an
    undeclared type comes back as undeclared.
    """
    ct = (profile or {}).get("company_type") or {}
    offering = str(ct.get("offering") or "").strip().lower()
    motion = str(ct.get("motion") or "").strip().lower()

    out = {"declared": False, "offering": offering or None, "motion": motion or None,
           "load_bearing": [], "discounted": [], "cautions": [], "notes": [], "missing": []}

    if offering not in OFFERING:
        out["missing"].append(
            "company_type.offering is %r, expected one of %s. Undeclared is not a default: "
            "most content advice assumes SaaS and transfers badly to anything else"
            % (ct.get("offering"), sorted(OFFERING)))
    if motion not in MOTION:
        out["missing"].append(
            "company_type.motion is %r, expected one of %s"
            % (ct.get("motion"), sorted(MOTION)))
    if out["missing"]:
        return out

    out["declared"] = True
    m, o = MOTION_RULES[motion], OFFERING_RULES[offering]
    out["load_bearing"] = list(m["load_bearing"])
    out["discounted"] = list(m["discounted"])
    out["notes"].append("proof for a %s buyer looks like: %s" % (offering, o["proof"]))
    out["notes"].append("who blocks a deal here: %s" % o["blockers"])
    out["notes"].append("artefact: %s" % m["artefact"])
    out["notes"].append("gate: %s" % o["gate"])
    if m["discounted"]:
        out["cautions"].append(
            "%s barely applies to a %s motion: %s"
            % (", ".join(m["discounted"]), motion.upper(), m["why_discounted"]))
    if o["channel"]:
        out["cautions"].append(o["channel"])

    # The combinations the research flags as behaving differently from the sum of their parts.
    if offering == "service" and motion in ("slg", "enterprise"):
        out["cautions"].append(
            "**Service sold through a committee is the case where a named person's channel is "
            "not optional.** The buyer is deciding whether they want these specific people in "
            "their business, and an organisation page cannot answer that question")
    if offering == "product" and motion == "enterprise":
        out["cautions"].append(
            "**Capital equipment through procurement: the claim regime is the strategy.** One "
            "unearned certification claim is a procurement exposure, and the people who catch it "
            "are the ones who were never in a sales conversation")
    return out


def check_calendar(profile: dict, jobs_present, carried=None) -> list:
    """Does this calendar do the jobs this company's buying model actually turns on?

    Returns findings, not a pass or fail. **A missing load-bearing job is the kind of gap that
    goes unnoticed for a quarter**, because nothing about a calendar full of good posts looks
    wrong until somebody asks who the late-stage work was for.

    `carried` is the set of jobs THIS CHANNEL can carry, and passing it matters. Without it the
    check asks a company-level question of a single channel and reports gaps that channel could
    never have filled: an executive profile carries no consensus-creation work by construction,
    so demanding it there produces a warning nobody can act on. **A warning that cannot be
    satisfied trains people to ignore the ones that can be.**

    Where a load-bearing job belongs to a different channel, that is said rather than silenced —
    it still has to happen somewhere, and the point of the check is that somebody looks.
    """
    imp = implications(profile)
    if not imp["declared"]:
        return ["company type is not declared, so no type check was run: %s"
                % "; ".join(imp["missing"])]
    present, out = set(jobs_present), []
    carried = set(carried) if carried is not None else None
    motion = (imp["motion"] or "").upper()

    for job in imp["load_bearing"]:
        if job in present:
            continue
        if carried is not None and job not in carried:
            out.append("%s is not carried by this channel at all, and a %s motion turns on it. "
                       "Check the channel that does carry it" % (job, motion))
        else:
            out.append("NO %s anywhere, and a %s motion turns on it" % (job, motion))

    for job in imp["discounted"]:
        if job in present:
            out.append("%s is scheduled, and a %s motion barely uses it. %s"
                       % (job, motion, MOTION_RULES[imp["motion"]]["why_discounted"]))
    return out


def describe(imp: dict) -> str:
    if not imp["declared"]:
        return "Company type NOT DECLARED\n  " + "\n  ".join(imp["missing"])
    lines = ["%s sold %s" % (imp["offering"], (imp["motion"] or "").upper()),
             "  jobs this buying model turns on: " + ", ".join(imp["load_bearing"])]
    if imp["discounted"]:
        lines.append("  jobs it barely uses:            " + ", ".join(imp["discounted"]))
    for n in imp["notes"]:
        lines.append("  - " + n)
    for c in imp["cautions"]:
        lines.append("  CAUTION: " + c)
    return "\n".join(lines)
