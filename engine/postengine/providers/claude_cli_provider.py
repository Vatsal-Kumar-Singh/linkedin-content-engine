"""Claude Code CLI adapter — runs on a Claude subscription, no API key.

Why this exists: the engine's default pairing is Anthropic (generator) + OpenAI
(judge), which needs two API keys. An operator with only a Claude Code
subscription has neither. This adapter shells out to the `claude` binary in
headless mode (`-p`), so the whole pipeline runs on the subscription already
paid for.

What it costs you: generator and judge end up on the same model FAMILY. That
weakens — it does not remove — the self-preference control the rubric relies on.
Use different MODELS for the two roles (opus vs sonnet) and read the
`judge_independence` field in the run report: it will say PARTIAL, not
INDEPENDENT. See registry.assert_independent.
"""
from __future__ import annotations

import base64
import os
import shutil
import subprocess
import tempfile
from typing import Any, Dict, List, Optional

from .base import Provider, ProviderError, TransientProviderError

BINARY = os.environ.get("CLAUDE_CLI_BINARY", "claude")

# The CLI writes quota exhaustion to stdout and exits non-zero. These are worth
# retrying (the limit resets); anything else is a genuine failure.
_TRANSIENT_MARKERS = (
    "usage limit reached",
    "session limit reached",
    "rate limit",
    "overloaded",
    "please try again",
    "timed out",
    "503",
    "529",
)

# Nothing here needs tools. Left enabled, the model may try to explore the repo
# instead of answering, which turns a completion into a multi-turn agent run.
_NO_TOOLS = ["Bash", "Edit", "Write", "Glob", "Grep", "WebFetch", "WebSearch", "Task"]


class ClaudeCLIProvider(Provider):
    name = "claude_cli"
    family = "anthropic"          # honest: these are Anthropic models
    supports_vision = True        # via a temp file + the Read tool

    @staticmethod
    def available() -> bool:
        return shutil.which(BINARY) is not None

    def __init__(self, model: str, **kwargs: Any) -> None:
        super().__init__(model, **kwargs)
        if not self.available():
            raise ProviderError(
                "the `claude` CLI is not on PATH. Install Claude Code, or set "
                "CLAUDE_CLI_BINARY to its full path.")
        self.timeout = int(self.options.get("timeout", 300))

    def complete(self, system: str, user: str, *, task: str = "",
                 images: Optional[List[str]] = None,
                 context: Optional[Dict[str, Any]] = None) -> str:
        tmp_paths: List[str] = []
        try:
            prompt = user
            cmd = [BINARY, "-p", "--model", self.model, "--output-format", "text"]

            if system:
                cmd += ["--system-prompt", system]

            if images:
                # The CLI has no base64 image channel, so decode to disk and let
                # the model read the files. Read is the only tool allowed.
                for i, b64 in enumerate(images):
                    fd, path = tempfile.mkstemp(prefix="fnx_critic_%d_" % i, suffix=".png")
                    with os.fdopen(fd, "wb") as fh:
                        fh.write(base64.b64decode(b64))
                    tmp_paths.append(path)
                listing = "\n".join("- %s" % p for p in tmp_paths)
                prompt = ("Read these rendered image(s) before answering:\n%s\n\n%s"
                          % (listing, user))
                cmd += ["--allowed-tools", "Read"]
            else:
                cmd += ["--disallowed-tools"] + _NO_TOOLS

            try:
                # The prompt goes on stdin, not argv: Windows caps a command line
                # at ~32k characters and these prompts routinely exceed it.
                proc = subprocess.run(
                    cmd, input=prompt, capture_output=True, text=True,
                    encoding="utf-8", errors="replace", timeout=self.timeout)
            except subprocess.TimeoutExpired:
                raise TransientProviderError(
                    "claude CLI timed out after %ds" % self.timeout)
            except OSError as exc:
                raise ProviderError("could not start the claude CLI: %s" % exc)

            out = (proc.stdout or "").strip()
            err = (proc.stderr or "").strip()

            if proc.returncode != 0:
                blob = ("%s\n%s" % (out, err)).lower()
                if any(m in blob for m in _TRANSIENT_MARKERS):
                    raise TransientProviderError(
                        "claude CLI unavailable: %s" % (out or err)[:300])
                raise ProviderError(
                    "claude CLI exited %d: %s" % (proc.returncode, (err or out)[:300]))

            if not out:
                raise TransientProviderError("claude CLI returned empty output")

            # A quota message can arrive on a zero exit code.
            if any(m in out.lower() for m in _TRANSIENT_MARKERS) and len(out) < 400:
                raise TransientProviderError("claude CLI: %s" % out[:300])

            return out
        finally:
            for p in tmp_paths:
                try:
                    os.unlink(p)
                except OSError:
                    pass

    def describe(self) -> Dict[str, Any]:
        d = super().describe()
        d["transport"] = "cli"
        d["auth"] = "subscription"
        return d
