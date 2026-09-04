"""Provider selection and the generator/judge independence guarantee."""
from __future__ import annotations

import os

from typing import Any, Dict, Optional, Tuple

from ..config import Config
from .base import Provider, ProviderError
from .mock import MockProvider

_REAL = {}


def _load_real(name: str):
    if name in _REAL:
        return _REAL[name]
    if name == "anthropic":
        from .anthropic_provider import AnthropicProvider as cls
    elif name == "openai":
        from .openai_provider import OpenAIProvider as cls
    elif name == "claude_cli":
        from .claude_cli_provider import ClaudeCLIProvider as cls
    else:
        raise ProviderError("unknown provider %r — add an adapter in postengine/providers/" % name)
    _REAL[name] = cls
    return cls


def available(name: str) -> bool:
    # Hermetic tests: whether a suite hits a real provider must not depend on
    # which credentials happen to exist on the machine running it. Without this,
    # having ANTHROPIC_API_KEY set — or the claude CLI on PATH — silently turns
    # unit tests into live API calls.
    if os.environ.get("ENGINE_FORCE_MOCK"):
        return False
    try:
        return _load_real(name).available()
    except ProviderError:
        return False


def describe_availability() -> Dict[str, bool]:
    return {n: available(n) for n in ("anthropic", "openai", "claude_cli")}


# Distinct pseudo-families keep the independence assertion meaningful offline.
_MOCK_FAMILY = {"generator": "mock-alpha", "judge": "mock-beta", "design_critic": "mock-gamma"}


def build(cfg: Config, role: str) -> Tuple[Provider, str]:
    """Return (provider, note). Falls back to mock only when configured to."""
    pc = cfg.provider_cfg(role)
    name = pc.pop("provider")
    model = pc.pop("model")
    pc.pop("family", None)
    kwargs = {k: v for k, v in pc.items() if k in ("temperature", "max_tokens")}

    if available(name):
        return _load_real(name)(model, **kwargs), ""

    if not (cfg.engine.get("providers") or {}).get("mock_when_no_credentials", True):
        raise ProviderError(
            "provider %r for role %r is unavailable and mock fallback is disabled. "
            "Set the API key in the environment (see .env.example)." % (name, role))

    return (MockProvider(model="mock-%s" % role, role=role,
                         family=_MOCK_FAMILY.get(role, "mock"), **kwargs),
            "%s unavailable (no credentials or SDK) — using mock" % name)


def assert_independent(cfg: Config, generator: Provider, judge: Provider) -> Optional[str]:
    """The judge must not be the same model family as the generator.

    Self-preference bias is real: a judge favours phrasing that sounds like
    itself, which is exactly the AI tell criterion C4 exists to catch.

    Three outcomes, because they are genuinely different risk levels:

      INDEPENDENT  different families. The control the rubric assumes.
      PARTIAL      same family, different model (e.g. opus judged by sonnet).
                   Self-preference is reduced, not removed: the models share a
                   training lineage and a house style. Usable — and the human
                   calibration pass is what quantifies the residual bias.
      DEGRADED     same family AND same model. The judge is grading its own
                   voice; the scores are not evidence of anything.

    Returns None when independent, or a note otherwise. Raises when the operator
    has not opted in.
    """
    same_family = generator.family == judge.family
    # The provider `name` is transport (api vs cli), not identity. Two roles on
    # the same family and the same model are the same judge whichever adapter
    # reached it.
    same_model = same_family and generator.model == judge.model
    if not same_family and not same_model:
        return None

    allowed = bool((cfg.engine.get("providers") or {}).get("allow_same_family"))
    detail = "generator=%s/%s judge=%s/%s" % (
        generator.family, generator.model, judge.family, judge.model)
    if not allowed:
        raise ProviderError(
            "generator and judge share a model family (%s). The rubric requires "
            "different families — self-preference bias is the exact AI tell C4 exists "
            "to catch. Configure a second provider, or set "
            "providers.allow_same_family: true in config/engine.yaml to override "
            "deliberately." % detail)
    if same_model:
        return "DEGRADED — generator and judge are the same model (%s). The judge is " \
               "grading its own voice; scores are not evidence and must not be used " \
               "for calibration." % detail
    return "PARTIAL — same family, different models (%s). Self-preference bias is " \
           "reduced but not removed. Calibrate against hand scores before trusting " \
           "any threshold derived from these numbers." % detail
