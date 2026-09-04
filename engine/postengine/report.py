"""Human-review package: the post as markdown, and the full run report."""
from __future__ import annotations

import datetime as _dt
from typing import Any, Dict, List

from .config import Config


def post_markdown(cfg: Config, result) -> str:
    it = result.final
    d = it.draft
    spec = result.spec
    pp = cfg.pain_point(spec.pain_point) or {}
    L: List[str] = []

    L.append("# %s — human review package" % result.run_id)
    L.append("")
    L.append("| | |")
    L.append("|---|---|")
    L.append("| Status | **%s** |" % result.status)
    L.append("| Pain point | %s — %s |" % (spec.pain_point, pp.get("title", "")))
    L.append("| Persona | %s |" % spec.persona)
    L.append("| Intent tier | %s — **human-confirmed: %s** |" % (
        spec.funnel_stage, "yes" if spec.tier_human_confirmed else "NO"))
    L.append("| Template / arc | %s / %s |" % (spec.template, spec.arc))
    L.append("| Metric labelling | %s |" % spec.metric_label)
    L.append("| Iterations | %d |" % len(result.iterations))
    L.append("| Judge | %d/12 · binary %.0f%% · %s |" % (
        it.judge.scored_total, it.binary_pass_rate() * 100, it.judge.verdict))
    L.append("| Rubric | v%s · claim rules v%s |" % (
        result.stamp["rubric_version"], result.stamp["claim_rules_version"]))
    L.append("| Generator / judge | %s / %s (%s) |" % (
        result.provider_info["generator"]["model"],
        result.provider_info["judge"]["model"],
        result.provider_info["judge_independence"]))
    if result.provider_info["generator"].get("mock"):
        L.append("| ⚠️ | **MOCK MODE** — no model credentials were present. Copy is fixture-composed, not model-written. |")
    L.append("")

    L.append("## Reviewer checklist")
    L.append("")
    L.append("- [ ] Intent tier is correct (the judge's C2 is advisory, never a clearance)")
    L.append("- [ ] Every figure carries its qualifier **on the creative**, not only in the caption")
    L.append("- [ ] Nothing internal has leaked into the copy")
    L.append("- [ ] The creative is legible on a phone")
    for r in result.reasons:
        L.append("- [ ] %s" % r)
    L.append("")

    L.append("---")
    L.append("")
    L.append("## The post")
    L.append("")
    L.append("```")
    L.append(d.hook)
    L.append("")
    L.append(d.body)
    if d.cta and d.cta != "none-by-design":
        L.append("")
        L.append(d.cta)
    L.append("```")
    L.append("")
    L.append("*%d characters · %d words*" % (len(d.caption_text()), len(d.caption_text().split())))
    L.append("")
    if d.first_comment:
        L.append("**First comment** (links never go in the body — ~60%% reach cost):")
        L.append("")
        L.append("> %s" % d.first_comment)
        L.append("")

    alts = [h for h in d.hook_alternatives if h.strip() != d.hook.strip()]
    if alts:
        L.append("**Hook alternatives considered**")
        L.append("")
        for h in alts:
            L.append("- %s" % h)
        L.append("")

    L.append("## The creative")
    L.append("")
    cd = result.creative_draft or d
    L.append("- **Focal:** %s" % cd.creative_headline)
    L.append("- **Supporting:** %s" % cd.creative_supporting_copy)
    if cd.creative_qualifier:
        L.append("- **Qualifier on the image:** %s" % cd.creative_qualifier)
    L.append("- **Concept:** %s" % cd.visual_concept)
    L.append("- **Alt text:** %s" % cd.alt_text)
    if result.creative.get("files"):
        L.append("- **Rendered:** %s" % ", ".join(result.creative["files"]))
    crit = (result.creative.get("design_critique") or {})
    if crit.get("status") == "ok":
        L.append("- **Design critic:** %s%s" % (
            crit.get("verdict", "?"),
            "  *(mock — geometry only, no vision model available)*" if crit.get("mock") else ""))
    n = result.creative.get("design_iterations")
    if n and n > 1:
        L.append("- **Creative iterations:** %d" % n)
        for h in result.creative.get("iterations") or []:
            for p_ in (h.get("problems_found") or [])[:3]:
                L.append("  - v%d · `%s` %s" % (h["variant"], p_.get("criterion"),
                                                str(p_.get("problem"))[:120]))
    L.append("")

    if cd.slides:
        L.append("### Slides")
        L.append("")
        for i, s in enumerate(cd.slides, 1):
            L.append("%d. **%s**%s" % (i, s.headline, ("  \n   %s" % s.body) if s.body else ""))
        L.append("")

    if d.claims_used:
        L.append("## Claims used")
        L.append("")
        L.append("| Claim | Qualifier | Source |")
        L.append("|---|---|---|")
        for i, c in enumerate(d.claims_used):
            q = d.claim_qualifiers[i] if i < len(d.claim_qualifiers) else "—"
            s = d.sources_used[i] if i < len(d.sources_used) else "—"
            L.append("| %s | %s | %s |" % (c, q, s))
        L.append("")

    L.append("## How this draft got here")
    L.append("")
    for i in result.iterations:
        L.append("**V%d** — deterministic %d pass / %d fail · judge %d/12 · %s"
                 % (i.n, i.deterministic.passed_count, i.deterministic.failed_count,
                    i.judge.scored_total, i.judge.verdict))
        if i.fixes_sent_to_generator:
            for f in i.fixes_sent_to_generator[:8]:
                L.append("  - `%s` %s" % (f.get("criterion"), f.get("problem", "")[:130]))
                if f.get("replacement"):
                    L.append("    → *%s*" % f["replacement"][:160].replace("\n", " "))
        L.append("")

    L.append("---")
    L.append("")
    L.append("*Generated %s. Nothing here is published until a person approves it.*"
             % _dt.datetime.now().strftime("%Y-%m-%d %H:%M"))
    return "\n".join(L)


def run_report(cfg: Config, result) -> Dict[str, Any]:
    spec = result.spec
    return {
        "run_id": result.run_id,
        "generated_at": _dt.datetime.now().isoformat(timespec="seconds"),
        "status": result.status,
        "reasons": result.reasons,
        "error": result.error,

        "provenance": dict(result.stamp, **{
            "prompts": ["prompts/generator.md", "prompts/generator_revision.md",
                        "prompts/judge.md", "prompts/design_critic.md"],
        }),
        "providers": result.provider_info,

        "content_spec": spec.to_dict(),
        "matrix_cell": {
            "pain_point": spec.pain_point, "family": spec.family, "persona": spec.persona,
            "funnel_stage": spec.funnel_stage, "content_type": spec.content_type,
            "angle": spec.angle, "template": spec.template, "arc": spec.arc,
            "hook": result.final.draft.hook if result.final and result.final.draft else None,
            "round": spec.round,
        },

        "iterations": [i.to_dict() for i in result.iterations],
        "iteration_count": len(result.iterations),
        "final": ({
            "draft": result.final.draft.to_dict(),
            "scored_total": result.final.judge.scored_total,
            "binary_pass_rate": round(result.final.binary_pass_rate(), 3),
            "verdict": result.final.judge.verdict,
            "deterministic_ok": result.final.deterministic.ok,
        } if result.final and result.final.draft else None),

        "creative": result.creative,

        "human_review": {
            "required": True,
            "tier_confirmed": spec.tier_human_confirmed,
            "note": "An LLM judge agrees with human reviewers around 85% of the time. "
                    "Enough to scale, not enough to trust unsupervised.",
        },
        "thresholds_applied": dict(cfg.pass_rules, mode=cfg.mode),
    }
