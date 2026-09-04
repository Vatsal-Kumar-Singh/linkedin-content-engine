"""OpenAI adapter — used as the JUDGE family so it never shares a family with the generator."""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from .base import Provider, ProviderError, TransientProviderError

ENV_KEY = "OPENAI_API_KEY"


class OpenAIProvider(Provider):
    name = "openai"
    family = "openai"
    supports_vision = True

    @staticmethod
    def available() -> bool:
        if not os.environ.get(ENV_KEY):
            return False
        try:
            import openai  # noqa: F401
        except ImportError:
            return False
        return True

    def __init__(self, model: str, **kwargs: Any) -> None:
        super().__init__(model, **kwargs)
        try:
            import openai
        except ImportError:
            raise ProviderError("the `openai` package is not installed (pip install openai)")
        key = os.environ.get(ENV_KEY)
        if not key:
            raise ProviderError("%s is not set" % ENV_KEY)
        self._openai = openai
        self._client = openai.OpenAI(api_key=key)

    def complete(self, system: str, user: str, *, task: str = "",
                 images: Optional[List[str]] = None,
                 context: Optional[Dict[str, Any]] = None) -> str:
        parts: List[Dict[str, Any]] = [{"type": "text", "text": user}]
        for b64 in (images or []):
            parts.append({"type": "image_url",
                          "image_url": {"url": "data:image/png;base64," + b64}})
        try:
            resp = self._client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                max_completion_tokens=self.max_tokens,
                response_format={"type": "json_object"},
                messages=[{"role": "system", "content": system},
                          {"role": "user", "content": parts}],
            )
        except (self._openai.APITimeoutError, self._openai.RateLimitError,
                self._openai.InternalServerError) as exc:
            raise TransientProviderError(str(exc))
        except self._openai.APIError as exc:
            raise ProviderError(str(exc))
        return resp.choices[0].message.content or ""
