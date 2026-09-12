"""Configuration loading. Nothing operational is hard-coded in application logic."""
from __future__ import annotations

import hashlib
import os
from typing import Any, Dict, List, Optional

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(ROOT, "config")


class ConfigError(RuntimeError):
    pass


def _read(name: str) -> Dict[str, Any]:
    path = os.path.join(CONFIG_DIR, name)
    if not os.path.exists(path):
        raise ConfigError("missing config file: config/%s" % name)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        raise ConfigError("config/%s is not valid YAML: %s" % (name, exc))
    if not isinstance(data, dict):
        raise ConfigError("config/%s did not parse to a mapping" % name)
    return data


def _sha256(path: str) -> Optional[str]:
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


class Config:
    """The whole configuration surface, loaded once per run."""

    def __init__(self) -> None:
        self.engine = _read("engine.yaml")
        self.brand = _read("brand.yaml")
        self.rules = _read("claim-rules.yaml")
        self.rubric = _read("rubric.yaml")
        self.registry = _read("registry.yaml")
        self.root = ROOT

        # Stamp the rubric hash so a score can always be traced to the criteria
        # that produced it, even if the markdown is later edited without a
        # version bump.
        rubric_path = os.path.join(ROOT, self.rubric.get("rubric_source", ""))
        self.rubric["rubric_sha256"] = _sha256(rubric_path)
        self._validate()

    # ------------------------------------------------------------------
    def _validate(self) -> None:
        mode = self.engine.get("mode")
        if mode not in ("calibration", "enforced"):
            raise ConfigError("engine.mode must be 'calibration' or 'enforced', got %r" % mode)
        pr = self.engine.get("pass_rules") or {}
        for k, lo, hi in (("minimum_binary_pass_rate", 0.0, 1.0),
                          ("minimum_quality_score", 0, 12),
                          ("maximum_iterations", 1, 20)):
            v = pr.get(k)
            if v is None:
                raise ConfigError("engine.pass_rules.%s is not set" % k)
            if not lo <= float(v) <= hi:
                raise ConfigError("engine.pass_rules.%s = %r is outside %s–%s" % (k, v, lo, hi))
        for role in ("generator", "judge"):
            if role not in (self.engine.get("providers") or {}):
                raise ConfigError("engine.providers.%s is not configured" % role)
        self._check_palette_references()

    # ------------------------------------------------------------------
    def _check_palette_references(self) -> None:
        """Every colour named anywhere in the brand file must exist in the palette.

        **This used to require three specific keys by name** (`brand_orange`, `ink_black`,
        `grey_light`), which were one company's colour names baked into the engine's contract.
        A different company with a perfectly good palette failed validation for not being that
        company, and the check still passed for a brand file whose `grounds` pointed at a colour
        that had been renamed.

        Referential integrity is both company-agnostic and strictly stronger: it catches the
        typo and the rename, which are the failures that actually happen, and it never asks
        anybody to own an orange.

        **Roles live in `grounds`, colours live in `palette`.** A template asks for the accent of
        the dark ground; it never asks for orange. That indirection is what lets one engine
        render for any brand, and this check is what keeps the two halves pointing at each other.
        """
        pal = self.brand.get("palette") or {}
        if not pal:
            raise ConfigError("brand.palette is empty. The renderer has no colours to work with")

        missing = []
        for ground, roles in (self.brand.get("grounds") or {}).items():
            for role, colour in (roles or {}).items():
                if colour not in pal:
                    missing.append("grounds.%s.%s -> %r" % (ground, role, colour))
        for name, spec in (self.brand.get("backgrounds") or {}).items():
            colour = (spec or {}).get("colour")
            if colour is not None and colour not in pal:
                missing.append("backgrounds.%s.colour -> %r" % (name, colour))

        if missing:
            raise ConfigError(
                "brand.yaml names %d colour(s) that are not in brand.palette:\n  %s\n"
                "Either add them to the palette or point these at a colour that exists."
                % (len(missing), "\n  ".join(missing)))

        # The renderer composes a ground from these four roles on every template. A brand file
        # missing one renders a card with a hole in it rather than failing, which is worse.
        for ground, roles in (self.brand.get("grounds") or {}).items():
            for role in ("bg", "fg", "accent", "structure"):
                if role not in (roles or {}):
                    raise ConfigError(
                        "brand.grounds.%s has no %r. Every ground needs bg, fg, accent and "
                        "structure, because every template composes all four." % (ground, role))

    # ------------------------------------------------------------------
    @property
    def mode(self) -> str:
        return self.engine["mode"]

    @property
    def pass_rules(self) -> Dict[str, Any]:
        return self.engine["pass_rules"]

    @property
    def max_iterations(self) -> int:
        return int(self.pass_rules["maximum_iterations"])

    @property
    def rubric_version(self) -> str:
        return str(self.rubric.get("rubric_version", "0.0.0"))

    @property
    def rules_version(self) -> str:
        return str(self.rules.get("version", "0.0.0"))

    def provider_cfg(self, role: str) -> Dict[str, Any]:
        return dict(self.engine["providers"][role])

    def pain_point(self, pid: str) -> Optional[Dict[str, Any]]:
        return (self.registry.get("pain_points") or {}).get(pid)

    def template_dir(self, template: str, arc: str) -> Optional[str]:
        router = self.engine.get("template_router") or {}
        key = "%s:%s" % (template, arc)
        by_arc = router.get("by_arc") or {}
        if key in by_arc:
            return by_arc[key]
        return (router.get("default") or {}).get(template)

    def rubric_text(self) -> str:
        path = os.path.join(self.root, self.rubric.get("rubric_source", ""))
        if not os.path.exists(path):
            raise ConfigError("rubric source not found: %s" % self.rubric.get("rubric_source"))
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()

    def stamp(self) -> Dict[str, Any]:
        """Provenance block written into every run report."""
        return {
            "engine_version": self.engine.get("engine_version"),
            "rubric_version": self.rubric_version,
            "rubric_sha256": self.rubric["rubric_sha256"],
            "claim_rules_version": self.rules_version,
            "mode": self.mode,
            "brand_status": self.brand.get("status"),
        }


_cached: Optional[Config] = None


def load(reload: bool = False) -> Config:
    global _cached
    if _cached is None or reload:
        _cached = Config()
    return _cached
