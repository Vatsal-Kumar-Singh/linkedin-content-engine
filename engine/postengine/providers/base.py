"""Provider interface. The engine is not coupled to any one vendor."""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class ProviderError(RuntimeError):
    """Non-retryable provider failure."""


class TransientProviderError(ProviderError):
    """Retryable: timeout, rate limit, 5xx, malformed JSON."""


class Provider:
    name = "base"
    family = "base"
    is_mock = False
    supports_vision = False

    def __init__(self, model: str, temperature: float = 0.7, max_tokens: int = 4000,
                 **kwargs: Any) -> None:
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.options = kwargs

    def complete(self, system: str, user: str, *, task: str = "",
                 images: Optional[List[str]] = None,
                 context: Optional[Dict[str, Any]] = None) -> str:
        raise NotImplementedError

    def describe(self) -> Dict[str, Any]:
        return {"provider": self.name, "model": self.model, "family": self.family,
                "mock": self.is_mock, "temperature": self.temperature}


def with_retry(fn, attempts: int, backoff: List[float], on_attempt=None):
    """Retry transient failures only. Never retries a genuine refusal or bad config."""
    last: Optional[Exception] = None
    for i in range(max(1, attempts)):
        try:
            return fn()
        except TransientProviderError as exc:
            last = exc
            if on_attempt:
                on_attempt(i + 1, exc)
            if i + 1 >= attempts:
                break
            time.sleep(backoff[min(i, len(backoff) - 1)] if backoff else 2)
        except ProviderError:
            raise
    raise ProviderError("provider failed after %d attempts: %s" % (attempts, last))
