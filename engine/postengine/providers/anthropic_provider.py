"""Anthropic adapter. Credentials come from the environment, never from config."""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from .base import Provider, ProviderError, TransientProviderError

ENV_KEY = "ANTHROPIC_API_KEY"


class AnthropicProvider(Provider):
    name = "anthropic"
    family = "anthropic"
    supports_vision = True

    @staticmethod
    def available() -> bool:
        if not os.environ.get(ENV_KEY):
            return False
        try:
            import anthropic  # noqa: F401
        except ImportError:
            return False
        return True

    def __init__(self, model: str, **kwargs: Any) -> None:
        super().__init__(model, **kwargs)
        try:
            import anthropic
        except ImportError:
            raise ProviderError("the `anthropic` package is not installed (pip install anthropic)")
        key = os.environ.get(ENV_KEY)
        if not key:
            raise ProviderError("%s is not set" % ENV_KEY)
        self._client = anthropic.Anthropic(api_key=key)

    def complete(self, system: str, user: str, *, task: str = "",
                 images: Optional[List[str]] = None,
                 context: Optional[Dict[str, Any]] = None) -> str:
        import anthropic

        content: List[Dict[str, Any]] = []
        for b64 in (images or []):
            content.append({"type": "image", "source": {
                "type": "base64", "media_type": "image/png", "data": b64}})
        content.append({"type": "text", "text": user})

        try:
            resp = self._client.messages.create(
                model=self.model,
                system=system,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[{"role": "user", "content": content}],
            )
        except (anthropic.APITimeoutError, anthropic.RateLimitError,
                anthropic.InternalServerError) as exc:
            raise TransientProviderError(str(exc))
        except anthropic.APIError as exc:
            raise ProviderError(str(exc))

        return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
