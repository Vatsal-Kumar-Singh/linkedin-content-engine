#!/usr/bin/env python3
"""Generate the calendar, and the post specs the pipeline runs from.

**This is the seam.** `config/registry.yaml` holds the pains, a profile holds the objectives and
the measured corpus, `decision/` decides, and the output is specs in `posts/` that `run.py`
already consumes unchanged. Nothing downstream had to be modified to accept them.

    python scripts/gen_calendar.py --profile example-meridian --channel clevel --slots 12
    python scripts/gen_calendar.py --profile example-meridian --channel clevel --write out

**The calendar is pains x angles, not pains x tiers.** `.claude/skills/build-content-calendar`
has the arithmetic: three pains at one post per tier is nine posts and four weeks of runway, and
what fills the gap is angles — the same pain approached a different way. Twenty-six angles are
mapped to buying jobs in `decision/scoring.py`, so the candidate set is large and the job is
ranking it rather than inventing it.

**It writes a brief, never copy.** `working_title` and `objective` are scaffolds naming the pain,
the angle and what the tier permits. The generator agent writes the post from that, and a human
reads the brief first. A calendar tool that invents titles is writing content nobody reviewed.
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml  # noqa: E402

from decision import channel as channel_mod  # noqa: E402
from decision import profile as profile_mod  # noqa: E402
from decision.scoring import (ANGLE_TO_JOB, ANGLE_TO_OTHER_OBJECTIVE, JOB_TO_TIER,  # noqa: E402
                              classify, gate, recommend, score_slot)

ENGINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# What the tier permits, from the skill's rule: TOFU = what is, MOFU = how to, BOFU = how WE.
# Written into every brief so the drafting model and the human reviewer read the same constraint.
TIER_RULE = {
    "TOFU": "Name the problem and stop. No product, no mechanism, no us. If this explains how WE "
            "do something it is not TOFU.",
    "MOFU": "Explain how the problem gets solved, in general. Mechanism is allowed; a pitch is "
            "not.",
    "BOFU": "How WE do it. Only schedule this where the reader cannot be reached any other way: "
            "it is for the person who blocks the deal and never takes a vendor call.",
}

# Angle -> the narrative arc the template router understands. Angles with no natural arc fall
# back to the default for their template, which the router already handles.
ANGLE_ARC = {
    "measured-scale": "single stat", "capability-proof": "single stat",
    "case-evidence": "stat arc", "how-it-rolled-out": "stat arc",
    "comparison": "before -> after", "myth-correction": "old way -> new way",
    "cost-of-inaction": "problem spiral", "failure-and-lesson": "problem spiral",
    "explainer": "explainer", "how-it-works": "explainer", "category-education": "explainer",
    "definitional": "explainer", "sizing": "explainer", "readiness-check": "explainer",
    "contrarian": "statement", "problem-reframe": "statement",
    "industry-reflection": "statement", "objection-handling": "statement",
    "change-scenario": "statement", "field-observation": "statement",
    "in-motion": "single stat", "single-vehicle": "single stat",
    "what-we-build": "statement", "safety-mechanism": "explainer",
    "cost-model": "before -> after", "supplier selection": "statement",
    "milestone": "single stat", "career-arc": "statement", "hiring": "statement",
}


def load_registry():
    with open(os.path.join(ENGINE, "config", "registry.yaml"), encoding="utf-8") as fh:
        return (yaml.safe_load(fh) or {}).get("pain_points") or {}


def candidates(pains, carried_jobs, persona, channel):
    """Every (pain, angle) pair whose job this channel carries. The whole grid, unranked."""
    out = []
    for pid, p in sorted(pains.items()):
        for angle in sorted(set(ANGLE_TO_JOB) | set(ANGLE_TO_OTHER_OBJECTIVE)):
            c = classify({"angle": angle})
            if c.get("objective"):
                continue                      # recruitment and the like: a separate budget
            if c["job"] not in carried_jobs:
                continue
            arc = ANGLE_ARC.get(angle, "statement")
            out.append({
                "pain": pid, "pain_title": (p or {}).get("title") or "",
                "pain_value": (p or {}).get("value") or "",
                "angle": angle, "job": c["job"], "tier": c["label"],
                "arc": arc, "persona": persona,
                # `who` marks a named person's own profile, and Gate reads it: a designed
                # carousel is banned there on production bandwidth. Without it the scorer
                # cheerfully recommended a carousel for every executive slot, because carousel
                # is the highest median in most corpora and nothing was stopping it.
                **({"who": "the named executive"} if channel == "clevel" else {}),
                # TEXT is the honest default. A template is only claimed once somebody has
                # decided a creative is worth making, and Lift reports what that is worth.
                "template": "CARD", "fmt": "text", "proof": "NONE",
            })
    return out


def to_spec(slot, n, prefix, rec=None):
    """One post spec. `rec` is the Lift recommendation, and it decides the template.

    **The format decides the template, and some formats this engine cannot render.** A photo
    album is photographs; no renderer makes those. Where that is what the corpus says wins, the
    spec ships on TEXT with a production note rather than claiming a creative nobody will make.
    """
    tier = slot["tier"]
    fmt = (rec or {}).get("format") or slot["fmt"]
    template = (rec or {}).get("template") or slot["template"]
    rendered = (rec or {}).get("rendered")
    needs = next((o["needs"] for o in (rec or {}).get("options", []) if o["fmt"] == fmt), None)

    brief = (
        "%s Angle: %s. The buying job is %s, so write for a reader doing that job. %s"
        % (slot["pain_title"] or "the pain named in the registry", slot["angle"], slot["job"],
           TIER_RULE.get(tier, ""))
    )
    if rendered is False:
        brief += (" CREATIVE: %s, which this engine does not render. Needs %s. Write the "
                  "caption; somebody else makes the picture." % (fmt, needs or "a person"))
    elif rendered:
        brief += " CREATIVE: %s, rendered from this spec." % fmt
    return {
        "id": "%s_%02d" % (prefix, n),
        "round": 1,
        "pain_point": slot["pain"],
        "family": slot["pain"][0],
        "persona": slot["persona"],
        "funnel_stage": tier,
        "content_type": slot["angle"],
        "angle": slot["angle"],
        "template": template,
        "arc": slot["arc"],
        "buying_job": slot["job"],
        "creative_format": fmt,
        "creative_produced_by": "this engine" if rendered else "a person",
        # Derived from the job, not guessed at — but a human still confirms it, because the
        # angle-to-job mapping is inferred rather than measured and says so.
        "tier_human_confirmed": False,
        "working_title": "[BRIEF, not a title] %s, approached as %s"
                         % (slot["pain_title"] or slot["pain"], slot["angle"]),
        "value_shown": slot["pain_value"] or "[from the registry: what we do about this pain]",
        "objective": brief,
        "metric_label": "no-hard-numbers",
        "constraints": [],
        "performance_tracking": True,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="example-meridian")
    ap.add_argument("--channel", default="clevel")
    ap.add_argument("--slots", type=int, default=12)
    ap.add_argument("--persona", default="the buyer named in the profile")
    ap.add_argument("--write", metavar="DIR", help="write specs into posts/<DIR>/")
    a = ap.parse_args()

    try:
        prof = profile_mod.load(a.profile)
    except Exception as e:
        sys.exit("could not load profile %r: %s" % (a.profile, e))

    rec = channel_mod.recommend_channels(prof)
    if rec["applies"] is None:
        print("The profile cannot say which channel carries what:")
        for m in rec["missing"]:
            print("   -", m)
        print("\nThese come from the intake. docs/decision/INTAKE.md")
        return 1
    if a.channel not in rec["channels"]:
        print("This profile gives no role to %r. It carries: %s"
              % (a.channel, ", ".join(rec["channels"])))
        return 1

    carried = set(rec["channels"][a.channel]["carries"])
    pains = load_registry()
    if not pains:
        sys.exit("config/registry.yaml has no pain_points. Phase 1 of docs/PLAYBOOK.md")

    cands = candidates(pains, carried, a.persona, a.channel)
    print("%d pains x %d angles this channel carries = %d candidates"
          % (len(pains), len({c["angle"] for c in cands}), len(cands)))

    scored = []
    for c in cands:
        r = score_slot(c, prof, a.channel)
        if not r["gate"]["pass"]:
            continue
        scored.append((r["fit"]["score"], c, r))

    withheld = [x for x in scored if x[0] is None]
    rankable = sorted([x for x in scored if x[0] is not None], key=lambda x: -x[0])

    if withheld and not rankable:
        print("\nNothing can be ranked: Fit is withheld on every candidate.")
        print("   %s" % "; ".join(withheld[0][2]["fit"]["missing"]))
        print("\nThe calendar below is therefore in registry order, not merit order.")
        rankable = [(None, c, r) for _, c, r in withheld]

    # ROUND-ROBIN BY PAIN, best unused angle each time. `build-content-calendar` is explicit:
    # organise by pain cluster, not by tier, because each pain gets a ladder and you publish
    # across them rather than running a TOFU month and then a MOFU month.
    #
    # It also fixes a worse problem. With no theme and no proof tier on a fresh candidate, Fit is
    # driven only by alignment, which is per-JOB — so every pain ties and a straight sort returns
    # the same angle once per pain. **Seven identical posts about seven different pains is the
    # calendar failing in the exact way the skill warns about**, and the tie is honest: nothing
    # in the profile distinguishes one pain from another yet. Where the scorer cannot
    # discriminate, rotate deliberately rather than letting the sort pick.
    by_pain = {}
    for score, c, r in rankable:
        by_pain.setdefault(c["pain"], []).append((score, c, r))

    chosen, used_angles, round_no = [], set(), 0
    while len(chosen) < a.slots and round_no < 40:
        progressed = False
        for pain in sorted(by_pain):
            if len(chosen) >= a.slots:
                break
            for item in by_pain[pain]:
                if item in chosen:
                    continue
                # Prefer an angle not used yet anywhere; fall back once every angle is spent.
                if item[1]["angle"] in used_angles and round_no < 20:
                    continue
                chosen.append(item)
                used_angles.add(item[1]["angle"])
                progressed = True
                break
        round_no += 1
        if not progressed:
            break

    print("\n%4s %-6s %-5s %-20s %-19s %-6s %-13s %s" %
          ("#", "pain", "tier", "job", "angle", "fit", "format", "creative"))
    print("-" * 108)
    not_rendered = 0
    for i, (score, c, r) in enumerate(chosen, 1):
        rc = recommend(c, a.channel, prof)
        best, tmpl, rend = rc["format"], rc["template"], rc["rendered"]
        if rend is False:
            not_rendered += 1
        who = {True: "%s, rendered" % tmpl, False: "%s, a person" % tmpl,
               None: "(no format measured)"}[rend]
        print("%4d %-6s %-5s %-20s %-19s %-6s %-13s %s"
              % (i, c["pain"], c["tier"], c["job"], c["angle"],
                 "%.3f" % score if score is not None else "  -", best or "-", who))

    if not_rendered:
        print("\n**%d of %d want a creative this engine does not make.** That is the corpus "
              "talking: photographs beat designed cards on most personal-profile corpora, and no "
              "renderer takes a photograph." % (not_rendered, len(chosen)))
        print("Those ship on TEXT, with the caption and a production note saying what to shoot.")

    if not a.write:
        print("\nNothing written. Re-run with --write <dir> to emit specs into posts/<dir>/.")
        return 0

    out = os.path.join(ENGINE, "posts", a.write)
    os.makedirs(out, exist_ok=True)
    for i, (_, c, _) in enumerate(chosen, 1):
        spec = to_spec(c, i, a.write, recommend(c, a.channel, prof))
        path = os.path.join(out, "%s.yaml" % spec["id"])
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("# GENERATED by scripts/gen_calendar.py. Edit the registry or the profile\n"
                     "# and regenerate; a hand-edited spec drifts from both.\n")
            yaml.safe_dump(spec, fh, sort_keys=False, allow_unicode=True, width=100)
    print("\nwrote %d specs -> posts/%s/" % (len(chosen), a.write))
    print("run one with:  ENGINE_FORCE_MOCK=1 python run.py --post %s_01" % a.write)
    return 0


if __name__ == "__main__":
    sys.exit(main())
