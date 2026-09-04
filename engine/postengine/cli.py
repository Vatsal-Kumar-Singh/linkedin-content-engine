"""Command line entry point."""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from typing import List, Optional

import yaml

from .config import Config, ConfigError, load as load_config
from .models import ContentSpec, SpecError
from .pipeline import Gauntlet
from .providers.base import ProviderError

BAR = "─" * 62


def emit(msg: str) -> None:
    print(msg, flush=True)


def find_spec(cfg: Config, ident: str) -> ContentSpec:
    base = os.path.join(cfg.root, (cfg.engine.get("paths") or {}).get("posts", "posts"))
    candidates = glob.glob(os.path.join(base, "**", "*.yaml"), recursive=True)
    for path in sorted(candidates):
        name = os.path.splitext(os.path.basename(path))[0]
        if name == ident:
            return _load(path)
    for path in sorted(candidates):
        data = yaml.safe_load(open(path, "r", encoding="utf-8")) or {}
        if str(data.get("id")) == ident or str(data.get("backlog_id")) == ident:
            return ContentSpec.from_dict(data)
    raise SpecError(
        "no content spec matches %r. Available: %s"
        % (ident, ", ".join(sorted(os.path.splitext(os.path.basename(p))[0]
                                   for p in candidates)) or "none"))


def _load(path: str) -> ContentSpec:
    with open(path, "r", encoding="utf-8") as fh:
        return ContentSpec.from_dict(yaml.safe_load(fh) or {})


def list_specs(cfg: Config) -> int:
    base = os.path.join(cfg.root, (cfg.engine.get("paths") or {}).get("posts", "posts"))
    rows = []
    for path in sorted(glob.glob(os.path.join(base, "**", "*.yaml"), recursive=True)):
        d = yaml.safe_load(open(path, "r", encoding="utf-8")) or {}
        rows.append((d.get("id", "?"), d.get("backlog_id", "-"), d.get("pain_point", "?"),
                     d.get("funnel_stage", "?"), d.get("template", "?"),
                     " ".join(str(d.get("working_title", "")).split())[:56]))
    print("\n  %-12s %-5s %-5s %-5s %-5s %s" % ("ID", "BLOG", "PAIN", "TIER", "TPL", "WORKING TITLE"))
    print("  " + BAR)
    for r in rows:
        print("  %-12s %-5s %-5s %-5s %-5s %s" % r)
    print()
    return 0


def header(cfg: Config, spec: ContentSpec, g: Gauntlet) -> None:
    pp = cfg.pain_point(spec.pain_point) or {}
    print("")
    print("  the product Content Engine")
    print("  " + BAR)
    print("  Post          %s%s" % (spec.id, ("  (%s)" % spec.backlog_id) if spec.backlog_id else ""))
    print("  Pain          %s — %s" % (spec.pain_point, pp.get("title", "")[:44]))
    print("  Stage         %s   Persona: %s" % (spec.funnel_stage, spec.persona))
    print("  Template      %s / %s" % (spec.template, (cfg.template_dir(spec.template, spec.arc) or "—").upper()))
    print("  Metric label  %s" % spec.metric_label)
    print("  Rubric        v%s   Claim rules v%s   Mode: %s"
          % (cfg.rubric_version, cfg.rules_version, cfg.mode.upper()))
    print("  Generator     %s  (%s)" % (g.gen_provider.model, g.gen_provider.family))
    print("  Judge         %s  (%s)  independence: %s"
          % (g.judge_provider.model, g.judge_provider.family, g.independence))
    for n in g.notes:
        print("  ! %s" % n)
    print("  " + BAR)


def footer(result) -> None:
    print("")
    print("  " + BAR)
    print("  STATUS        %s" % result.status)
    for r in result.reasons:
        print("    · %s" % r)
    if result.creative:
        c = result.creative
        print("  CREATIVE      %s  %s" % (c.get("status"), c.get("dimensions", "")))
        for f in c.get("files") or []:
            print("                %s" % f)
        for p in c.get("fit_problems") or []:
            print("    ! %s" % p)
    print("  OUTPUT        %s/" % os.path.relpath(result.directory, os.getcwd()))
    print("  " + BAR)
    print("")


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        prog="run.py", description="the product LinkedIn content & creative engine")
    ap.add_argument("--post", help="content spec id, e.g. round1_01 (or a backlog id like T1)")
    ap.add_argument("--round", type=int, help="run every spec in a round")
    ap.add_argument("--list", action="store_true", help="list available content specs")
    ap.add_argument("--no-render", action="store_true", help="skip creative rendering")
    ap.add_argument("--animate", action="store_true",
                    help="also emit a looping motion asset for single-card posts "
                         "(GIF, or MP4 if ffmpeg is installed). Carousels stay static.")
    ap.add_argument("--mode", choices=["calibration", "enforced"], help="override engine.mode")
    ap.add_argument("--max-iterations", type=int, help="override the iteration cap")
    args = ap.parse_args(argv)

    try:
        cfg = load_config()
    except ConfigError as exc:
        print("configuration error: %s" % exc, file=sys.stderr)
        return 2

    if args.mode:
        cfg.engine["mode"] = args.mode
    if args.max_iterations:
        cfg.engine["pass_rules"]["maximum_iterations"] = args.max_iterations
    if args.animate:
        cfg.engine.setdefault("creative", {})["animate"] = True

    if args.list or (not args.post and not args.round):
        return list_specs(cfg)

    try:
        specs = ([find_spec(cfg, args.post)] if args.post else
                 _round_specs(cfg, args.round))
    except SpecError as exc:
        print("  %s" % exc, file=sys.stderr)
        return 2

    try:
        g = Gauntlet(cfg, emit=emit)
    except ProviderError as exc:
        print("\n  provider error: %s\n" % exc, file=sys.stderr)
        return 3

    worst = 0
    for spec in specs:
        header(cfg, spec, g)
        result = g.run(spec, render=not args.no_render)
        footer(result)
        if result.status in ("ERROR",):
            worst = max(worst, 1)
    return worst


def _round_specs(cfg: Config, rnd: int) -> List[ContentSpec]:
    base = os.path.join(cfg.root, (cfg.engine.get("paths") or {}).get("posts", "posts"))
    out = []
    for path in sorted(glob.glob(os.path.join(base, "**", "*.yaml"), recursive=True)):
        d = yaml.safe_load(open(path, "r", encoding="utf-8")) or {}
        if int(d.get("round") or 0) == rnd:
            out.append(ContentSpec.from_dict(d))
    if not out:
        raise SpecError("no content specs found for round %s" % rnd)
    return out
