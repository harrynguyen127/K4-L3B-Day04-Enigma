from __future__ import annotations

import os
import re
from typing import Any

from providers.base import ModelResponse
from providers.ollama_provider import OllamaProvider


ASSET_ID = re.compile(r"\b(?:LT|DT|PR)-\d+\b", re.IGNORECASE)
EMPLOYEE_ID = re.compile(r"\bEMP-\d+\b", re.IGNORECASE)
CANCEL_WORDS = ("cancel", "stop", "dừng", "hủy", "không tạo", "do nothing")
OUT_OF_SCOPE_WORDS = ("công thức", "nấu", "phở", "recipe", "movie", "game", "rest api", "python")
DEVICE_WORDS = ("laptop", "desktop", "thiết bị", "device", "máy", "wi-fi", "wifi")
EMPLOYEE_WORDS = ("nhân viên", "employee", "tài khoản", "account", "sales")


class OllamaRouterProvider:
    """Use a small local model first and escalate risky tool calls to a larger one."""

    default_model = "qwen2.5:3b"

    def __init__(self) -> None:
        self.primary = OllamaProvider()
        self.fallback = OllamaProvider()
        self.fallback_model = os.getenv("OLLAMA_FALLBACK_MODEL", "qwen2.5:7b")

    def complete(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        *,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: Any | None = None,
    ) -> ModelResponse:
        primary_model = model or self.default_model
        response = self.primary.complete(
            messages, tools, model=primary_model, temperature=temperature, tool_choice=tool_choice
        )
        if not self._needs_fallback(messages, response, tool_choice):
            return response

        fallback = self.fallback.complete(
            messages, tools, model=self.fallback_model, temperature=temperature, tool_choice=tool_choice
        )
        fallback.raw = {
            "router": {"primary_model": primary_model, "fallback_model": self.fallback_model},
            "response": fallback.raw,
        }
        return fallback

    def _needs_fallback(
        self,
        messages: list[dict[str, str]],
        response: ModelResponse,
        tool_choice: Any | None,
    ) -> bool:
        conversation = "\n".join(item["content"] for item in messages if item["role"] == "user").lower()
        latest = conversation.rsplit("latest user turn to answer now:", 1)[-1].strip()

        if any(word in latest for word in CANCEL_WORDS) and response.tool_calls:
            return True
        if any(word in latest for word in OUT_OF_SCOPE_WORDS) and response.tool_calls:
            return True
        if self._missing_required_identifier(conversation, latest):
            return True
        if "demo" in latest or "qa environment" in latest:
            return True
        if self._has_invalid_tool_args(response):
            return True
        if tool_choice == "required" and not response.tool_calls:
            return True
        if self._needs_service_and_device(latest) and len(response.tool_calls) < 2:
            return True
        return False

    @staticmethod
    def _missing_required_identifier(conversation: str, latest: str) -> bool:
        if any(word in latest for word in DEVICE_WORDS) and not ASSET_ID.search(conversation):
            return True
        if any(word in latest for word in EMPLOYEE_WORDS) and not EMPLOYEE_ID.search(conversation):
            return True
        return False

    @staticmethod
    def _has_invalid_tool_args(response: ModelResponse) -> bool:
        for call in response.tool_calls:
            if call.name == "inspect_device" and not ASSET_ID.fullmatch(str(call.args.get("asset_id", ""))):
                return True
            if call.name == "lookup_user" and not EMPLOYEE_ID.fullmatch(str(call.args.get("employee_id", ""))):
                return True
            if call.name == "check_service_status" and call.args.get("environment") not in {"production", "staging"}:
                return True
        return False

    @staticmethod
    def _needs_service_and_device(latest: str) -> bool:
        return "vpn" in latest and any(word in latest for word in ("cả", "both", "and")) and "production" in latest
