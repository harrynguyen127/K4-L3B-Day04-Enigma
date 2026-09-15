from __future__ import annotations

import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from providers.base import ModelResponse, ToolCall


class OllamaProvider:
    """Native local Ollama chat API with normalized tool calls."""

    default_model = None

    def __init__(self) -> None:
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")

    def complete(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        *,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: Any | None = None,
    ) -> ModelResponse:
        if not model:
            raise RuntimeError("Missing Ollama model. Pass --model qwen2.5:3b")
        if tool_choice not in (None, "auto", "required", "none"):
            raise ValueError("Ollama provider does not support forced named tool choices")
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
            "keep_alive": "5m",
            "options": {"temperature": temperature, "num_ctx": 8192},
        }
        # Native Ollama has no required-tool setting; preserve model-selected calls.
        if tools and tool_choice != "none":
            payload["tools"] = tools
        request = Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=300) as response:
                raw = json.load(response)
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Ollama HTTP {exc.code}: {detail}") from exc
        except URLError as exc:
            raise RuntimeError(f"Cannot reach Ollama at {self.base_url}: {exc.reason}") from exc
        if raw.get("error"):
            raise RuntimeError(f"Ollama: {raw['error']}")
        message = raw["message"]
        calls: list[ToolCall] = []
        for call in message.get("tool_calls") or []:
            function = call["function"]
            arguments = function.get("arguments", {})
            if isinstance(arguments, str):
                arguments = json.loads(arguments)
            if not isinstance(arguments, dict):
                raise ValueError("Ollama tool arguments must be a JSON object")
            calls.append(ToolCall(name=function["name"], args=arguments))
        return ModelResponse(text=message.get("content"), tool_calls=calls, raw=raw)
