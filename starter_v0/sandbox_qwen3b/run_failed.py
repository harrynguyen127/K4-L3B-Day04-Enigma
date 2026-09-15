from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from env_loader import load_lab_env
from providers.ollama_provider import OllamaProvider
from run_eval import case_messages, evaluate_phase_b, summarize
from tools import load_tool_declarations


def main() -> None:
    parser = argparse.ArgumentParser(description="Isolated structured-plan eval of failed cases only.")
    parser.add_argument("--model", required=True)
    parser.add_argument("--failed-run", type=Path, action="append", required=True)
    args = parser.parse_args()
    load_lab_env(ROOT)
    failed_ids: set[str] = set()
    for path in args.failed_run:
        run = json.loads(path.read_text(encoding="utf-8"))
        failed_ids.update(item["id"] for item in run["results"] if not item["result"]["passed"])
    dataset = json.loads((ROOT / "data/eval_base.json").read_text(encoding="utf-8"))
    cases = [case for case in dataset["cases"] if case["id"] in failed_ids]
    if len(cases) != len(failed_ids):
        raise ValueError("Some failed case IDs are absent from eval_base.json")
    declarations = load_tool_declarations(ROOT / "artifacts/tools.yaml")
    prompt_path = Path(__file__).with_name("planner_prompt.md")
    prompt = prompt_path.read_text(encoding="utf-8")
    provider = OllamaProvider()

    def generate(messages, schema):
        payload = {
            "model": args.model, "messages": messages, "format": schema,
            "stream": False, "keep_alive": "5m",
            "options": {"temperature": 0, "num_ctx": 8192},
        }
        request = Request(
            provider.base_url + "/api/chat", data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST",
        )
        with urlopen(request, timeout=300) as response:
            raw = json.load(response)
        return json.loads(raw["message"]["content"]), raw

    router_prompt = Path(__file__).with_name("router_prompt.md").read_text(encoding="utf-8")
    router_properties = {key: {"type": "boolean"} for key in (
        "in_scope", "stop", "device_diagnostic", "employee_lookup", "needs_ticket_confirmation",
    )}
    router_properties.update({"environment": {"type": "string"}, "reply": {"type": "string"}})
    router_schema = {
        "type": "object", "properties": router_properties,
        "required": list(router_properties), "additionalProperties": False,
    }
    results = []
    for case in cases:
        print(f"Running {case['id']}...", flush=True)
        # Only input context is sent to the model; expected calls stay in the evaluator.
        context = case.get("turns") or case_messages(case)
        route, router_raw = generate([{"role": "system", "content": router_prompt}, *context], router_schema)
        user_text = "\n".join(turn["content"] for turn in context if turn["role"] == "user")
        asset_ids = re.findall(r"\b(?:LT|DT|PR)-\d+\b", user_text, re.IGNORECASE)
        employee_ids = re.findall(r"\bEMP-\d+\b", user_text, re.IGNORECASE)
        # Router facts must be grounded in user text, not invented by the model.
        grounding_issues = []
        environment = route["environment"].strip()
        explicit_environments = re.findall(
            r"(?:môi trường|\benvironment)\s*[:=]?\s+([^\s,.;:?!]+)",
            user_text, re.IGNORECASE,
        )
        if explicit_environments:
            # Preserve the literal label instead of a router translation/paraphrase.
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
            selected = json.loads(json.dumps(declarations))
            response_type = {
                "missing_asset": "text", "missing_employee": "text",
                "ambiguous_environment": "choice", "confirm_ticket": "yes_no",
            }.get(mode)
            if response_type:
                selected = [tool for tool in selected if tool["name"] == "clarify"]
                parameters = selected[0]["parameters"]
                parameters["properties"]["response_type"] = {"const": response_type}
                if mode == "ambiguous_environment":
                    parameters["properties"]["options"] = {"const": ["production", "staging"]}
                    parameters["required"].append("options")
                else:
                    parameters["properties"].pop("options", None)
                parameters["additionalProperties"] = False
            else:
                selected = [tool for tool in selected if tool["name"] != "clarify"]
            variants = [{
                "type": "object", "properties": {
                    "name": {"const": tool["name"]}, "args": tool["parameters"],
                }, "required": ["name", "args"], "additionalProperties": False,
            } for tool in selected]
            schema = {
                "type": "object", "properties": {
                    "calls": {"type": "array", "minItems": 1, "items": {"anyOf": variants}},
                    "reply": {"type": "string"},
                }, "required": ["calls", "reply"], "additionalProperties": False,
            }
            instruction = prompt + "\nRouting decision: " + mode
            instruction += "\nIDs actually supplied in chronological order: " + json.dumps({
                "assets": asset_ids, "employees": employee_ids,
            })
            instruction += "\nFor a corrected device use the newest corrected ID, not a replaced earlier ID."
            instruction += "\nAvailable tool contracts:\n" + json.dumps(selected, ensure_ascii=False)
            plan, raw = generate([{"role": "system", "content": instruction}, *context], schema)
        result = evaluate_phase_b(case, plan["calls"], plan["reply"])
        results.append({
            "id": case["id"], "phase": case["phase"], "input": case.get("query", case.get("turns")),
            "expect": case["expect"], "is_multiturn": "turns" in case,
            "result": result, "raw": raw, "route": route, "router_raw": router_raw,
            "grounding_issues": grounding_issues,
        })
        print(json.dumps({"id": case["id"], "passed": result["passed"], "calls": plan["calls"], "failures": result["failures"]}), flush=True)
    report = {
        "model": args.model, "mode": "sandbox_two_stage_plan_no_tool_execution",
        "source_runs": [str(path) for path in args.failed_run],
        "prompt": prompt_path.read_text(encoding="utf-8"), "router_prompt": router_prompt, "tools": declarations,
        "summary": summarize(results), "results": results,
    }
    output = Path(__file__).with_name("focused_" + datetime.now().strftime("%Y%m%dT%H%M%S%f") + ".json")
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report["summary"]), flush=True)
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()
