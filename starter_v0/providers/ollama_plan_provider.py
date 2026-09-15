from __future__ import annotations

import copy
import json
import re
from typing import Any
from urllib.request import Request, urlopen

from providers.base import ModelResponse, ToolCall
from providers.ollama_provider import OllamaProvider


class OllamaPlanProvider(OllamaProvider):
    """Classify and plan with one selected local model before executing tools."""

    def __init__(self, router_prompt: str) -> None:
        super().__init__()
        self.router_prompt = router_prompt

    def _generate(self, messages, schema, model, temperature):
        payload = {
            "model": model, "messages": messages, "format": schema,
            "stream": False, "keep_alive": "5m",
            "options": {"temperature": temperature, "num_ctx": 8192},
        }
        request = Request(
            self.base_url + "/api/chat", data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST",
        )
        with urlopen(request, timeout=300) as response:
            raw = json.load(response)
        return json.loads(raw["message"]["content"]), raw

    def complete(
        self, messages: list[dict[str, str]], tools: list[dict[str, Any]] | None = None,
        *, model: str | None = None, temperature: float = 0.0,
        tool_choice: Any | None = None,
    ) -> ModelResponse:
        if not model:
            raise RuntimeError("Missing Ollama model. Pass --model qwen2.5:3b")
        if tool_choice not in (None, "auto"):
            raise ValueError("Planned pipeline decides tool use without forced tool_choice")
        prompt = "\n".join(item["content"] for item in messages if item["role"] == "system")
        context = [item for item in messages if item["role"] != "system"]
        declarations = [copy.deepcopy(tool["function"]) for tool in tools or []]
        router_properties = {key: {"type": "boolean"} for key in (
            "in_scope", "stop", "device_diagnostic", "employee_lookup", "needs_ticket_confirmation",
        )}
        router_properties.update({"environment": {"type": "string"}, "reply": {"type": "string"}})
        router_schema = {
            "type": "object", "properties": router_properties,
            "required": list(router_properties), "additionalProperties": False,
        }
        route, router_raw = self._generate(
            [{"role": "system", "content": self.router_prompt}, *context],
            router_schema, model, temperature,
        )
        user_text = "\n".join(item["content"] for item in context if item["role"] == "user")
        latest = next((item["content"] for item in reversed(context) if item["role"] == "user"), "")
        latest_lower = latest.casefold()
        asset_ids = re.findall(r"\b(?:LT|DT|PR)-\d+\b", user_text, re.IGNORECASE)
        employee_ids = re.findall(r"\bEMP-\d+\b", user_text, re.IGNORECASE)
        grounding_issues = []
        # Apply general request constraints before trusting model classifications.
        scope_patterns = {
            "vpn": r"\bvpn\b", "network": r"wi-fi|wireless|\bnetwork\b",
            "security": r"\bsecurity\b|encryption|endpoint|patches",
            "hardware": r"\bhardware\b|battery|\bdisk\b|memory|pin máy",
            "software": r"\bsoftware\b|\bapp\b",
        }
        scope = next((name for name, pattern in scope_patterns.items() if re.search(pattern, latest_lower)), None)
        if scope and asset_ids and re.search(r"kiểm tra|check|snapshot|so sánh|compare", latest_lower):
            route["in_scope"] = True
            route["device_diagnostic"] = True
        if re.search(r"bạn là gì|what are you|what can you|có thể hỗ trợ những|your capabilities", latest_lower):
            route["stop"] = True
        if re.search(r"^(?:viết|write|build|implement)\b", latest_lower) and re.search(r"rest api|python|application|ứng dụng", latest_lower):
            route["in_scope"] = False
            if not route["reply"]:
                route["reply"] = "Tôi hỗ trợ IT nội bộ, không viết ứng dụng theo yêu cầu này."
        report_only = bool(re.search(r"báo cáo|\breport\b", latest_lower) and re.search(r"finding|format|trình bày|định dạng", latest_lower))
        if report_only:
            route["in_scope"] = True
            route["device_diagnostic"] = False
            route["employee_lookup"] = False
        title_match = re.search(r"(?:tên|title|named)\s*[:=]?\s*(['\"])(.*?)\1", latest, re.IGNORECASE)
        environment = route["environment"].strip()
        explicit_environments = re.findall(
            r"(?:môi trường|\benvironment)\s*[:=]?\s+([^\s,.;:?!]+)",
            user_text, re.IGNORECASE,
        )
        explicit_environments = [value for value in explicit_environments if value.casefold() not in {"nào", "này", "đó", "which", "any", "all"}]
        if explicit_environments:
            environment = explicit_environments[-1].strip("\"'")
        if environment and environment.casefold() not in user_text.casefold():
            grounding_issues.append("Router environment is absent from user text")
            environment = ""
        confirms_ticket = route["needs_ticket_confirmation"]
        if confirms_ticket and not re.search(r"\bticket\b", user_text, re.IGNORECASE):
            grounding_issues.append("Router requests ticket confirmation without a ticket request")
            confirms_ticket = False
        if not route["in_scope"] or route["stop"]:
            mode = "no_tool"
        elif route["device_diagnostic"] and not asset_ids:
            mode = "missing_asset"
        elif route["employee_lookup"] and not employee_ids:
            mode = "missing_employee"
        elif environment and environment.lower() not in ("production", "staging"):
            mode = "ambiguous_environment"
        elif confirms_ticket:
            mode = "confirm_ticket"
        else:
            mode = "tools"
        route["mode"] = mode
        raw = None
        if mode == "no_tool":
            plan = {"calls": [], "reply": route["reply"]}
        else:
            selected = declarations
            minimum_calls = 1
            response_type = {
                "missing_asset": "text", "missing_employee": "text",
                "ambiguous_environment": "choice", "confirm_ticket": "yes_no",
            }.get(mode)
            if response_type:
                selected = [tool for tool in selected if tool["name"] == "clarify"]
                if not selected:
                    raise ValueError("Planned clarification requires a declared clarify tool")
                parameters = selected[0]["parameters"]
                parameters["properties"]["response_type"] = {"const": response_type}
                if mode == "ambiguous_environment":
                    parameters["properties"]["options"] = {"const": ["production", "staging"]}
                    parameters["required"].append("options")
                else:
                    parameters["properties"].pop("options", None)
                parameters["additionalProperties"] = False
            else:
                guidance = bool(re.search(r"hướng dẫn|how-to|guidance|tìm bài", latest_lower))
                shared_status = bool(
                    re.search(r"\bvpn\b|\bemail\b|wi-fi|\bwifi\b|\bsso\b|printing", latest_lower)
                    and (re.search(r"trạng thái|\bstatus\b|availability", latest_lower)
                         or (re.search(r"production|staging", latest_lower) and re.search(r"\bvà\b|\band\b|\bboth\b|\bcả\b", latest_lower)))
                )
                allowed = set()
                if report_only:
                    allowed.add("format_incident_report")
                else:
                    if route["device_diagnostic"]:
                        allowed.add("inspect_device")
                    if route["employee_lookup"]:
                        allowed.add("lookup_user")
                    if guidance:
                        allowed.add("search_kb")
                    if shared_status:
                        allowed.add("check_service_status")
                    if allowed:
                        minimum_calls = len(allowed)
                    if not allowed:
                        allowed = {tool["name"] for tool in selected} - {"clarify", "format_incident_report", "inspect_device", "lookup_user"}
                    if not re.search(r"\bticket\b", user_text, re.IGNORECASE):
                        allowed.discard("create_ticket")
                selected = [tool for tool in selected if tool["name"] in allowed]
                if re.search(r"so sánh|compare", latest_lower):
                    if allowed == {"inspect_device"}:
                        minimum_calls = max(1, len(set(asset_ids)))
                    if allowed == {"check_service_status"}:
                        minimum_calls = max(1, len(set(re.findall(r"\b(?:production|staging)\b", latest_lower))))
                for tool in selected:
                    properties = tool["parameters"].setdefault("properties", {})
                    if tool["name"] == "inspect_device" and scope:
                        properties["check"] = {"const": scope}
                    if tool["name"] == "search_kb":
                        topic = latest if re.search(r"outlook|email|wi-fi|wireless|vpn|printer|printing|password|mfa|account", latest_lower) else user_text
                        category = next((value for pattern, value in (
                            (r"outlook|email|mailbox", "email"), (r"wi-fi|wireless", "wifi"),
                            (r"\bvpn\b", "vpn"), (r"printer|printing", "printing"),
                            (r"password|mfa|account", "account"),
                        ) if re.search(pattern, topic, re.IGNORECASE)), None)
                        if category:
                            properties["category"] = {"const": category}
                    if tool["name"] == "format_incident_report":
                        if title_match:
                            properties["incident_title"] = {"const": title_match.group(2)}
                            tool["parameters"]["required"] = list(dict.fromkeys([*tool["parameters"]["required"], "incident_title"]))
                        template = next((value for pattern, value in (
                            (r"handoff", "handoff"), (r"technical|kỹ thuật", "technical"), (r"brief", "brief"),
                        ) if re.search(pattern, latest_lower)), None)
                        if template:
                            properties["template"] = {"const": template}
            variants = [{
                "type": "object", "properties": {
                    "name": {"const": tool["name"]}, "args": tool["parameters"],
                }, "required": ["name", "args"], "additionalProperties": False,
            } for tool in selected]
            schema = {
                "type": "object", "properties": {
                    "calls": {"type": "array", "minItems": minimum_calls, "items": {"anyOf": variants}},
                    "reply": {"type": "string"},
                }, "required": ["calls", "reply"], "additionalProperties": False,
            }
            instruction = prompt + "\nRouting decision: " + mode
            instruction += "\nIDs actually supplied in chronological order: " + json.dumps({
                "assets": asset_ids, "employees": employee_ids,
            })
            instruction += "\nFor a corrected device use the newest corrected ID, not a replaced earlier ID."
            instruction += "\nAvailable tool contracts:\n" + json.dumps(selected, ensure_ascii=False)
            plan, raw = self._generate(
                [{"role": "system", "content": instruction}, *context], schema, model, temperature,
            )
        return ModelResponse(
            text=plan["reply"],
            tool_calls=[ToolCall(name=call["name"], args=call["args"]) for call in plan["calls"]],
            raw={"pipeline": "planned", "model": model, "route": route,
                 "grounding_issues": grounding_issues, "router_raw": router_raw, "planner_raw": raw},
        )
