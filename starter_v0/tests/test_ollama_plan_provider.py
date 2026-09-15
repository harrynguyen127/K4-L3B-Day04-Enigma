import copy
import unittest
from unittest.mock import Mock

from providers.ollama_plan_provider import OllamaPlanProvider


class PlannedProviderTests(unittest.TestCase):
    def setUp(self):
        self.provider = OllamaPlanProvider("router instructions")
        self.route = {
            "in_scope": True, "stop": False, "device_diagnostic": False,
            "employee_lookup": False, "needs_ticket_confirmation": False,
            "environment": "", "reply": "",
        }
        self.tools = [{"type": "function", "function": {
            "name": "clarify", "parameters": {
                "type": "object", "properties": {
                    "question": {"type": "string"},
                    "response_type": {"enum": ["text", "choice", "yes_no"]},
                    "options": {"type": "array", "items": {"type": "string"}},
                }, "required": ["question", "response_type"],
            },
        }}, {"type": "function", "function": {
            "name": "inspect_device", "parameters": {"type": "object"},
        }}]

    def complete(self, content):
        return self.provider.complete(
            [{"role": "system", "content": "planner instructions"},
             {"role": "user", "content": content}], self.tools, model="qwen2.5:3b",
        )

    def test_stop_skips_planning(self):
        self.route.update(stop=True, reply="Stopped")
        self.provider._generate = Mock(return_value=(self.route, {}))
        result = self.complete("Stop the previous task")
        self.assertEqual(result.tool_calls, [])
        self.assertEqual(self.provider._generate.call_count, 1)

    def test_missing_id_narrows_schema_without_mutating_tools(self):
        self.route["device_diagnostic"] = True
        original = copy.deepcopy(self.tools)
        self.provider._generate = Mock(side_effect=[
            (self.route, {}),
            ({"calls": [{"name": "clarify", "args": {
                "question": "Asset ID?", "response_type": "text",
            }}], "reply": ""}, {}),
        ])
        result = self.complete("Check my laptop")
        schema = self.provider._generate.call_args_list[1].args[1]
        variant = schema["properties"]["calls"]["items"]["anyOf"][0]
        self.assertEqual(variant["properties"]["name"], {"const": "clarify"})
        self.assertEqual(variant["properties"]["args"]["properties"]["response_type"], {"const": "text"})
        self.assertEqual(result.raw["route"]["mode"], "missing_asset")
        self.assertEqual(self.tools, original)

    def test_literal_environment_survives_router_paraphrase(self):
        self.route["environment"] = "sandbox of QA"
        self.provider._generate = Mock(side_effect=[
            (self.route, {}),
            ({"calls": [{"name": "clarify", "args": {
                "question": "Environment?", "response_type": "choice",
                "options": ["production", "staging"],
            }}], "reply": ""}, {}),
        ])
        result = self.complete("Check email in environment sandbox")
        self.assertEqual(result.raw["route"]["mode"], "ambiguous_environment")
        schema = self.provider._generate.call_args_list[1].args[1]
        parameters = schema["properties"]["calls"]["items"]["anyOf"][0]["properties"]["args"]
        self.assertEqual(parameters["properties"]["options"], {"const": ["production", "staging"]})

    def test_hallucinated_ticket_does_not_force_confirmation(self):
        self.route.update(device_diagnostic=True, needs_ticket_confirmation=True)
        self.provider._generate = Mock(side_effect=[
            (self.route, {}),
            ({"calls": [{"name": "inspect_device", "args": {
                "asset_id": "DT-901", "check": "hardware",
            }}], "reply": ""}, {}),
        ])
        result = self.complete("Check battery on DT-901")
        self.assertEqual(result.raw["route"]["mode"], "tools")
        self.assertTrue(result.raw["grounding_issues"])

    def test_forced_choice_is_rejected_instead_of_using_eval_signal(self):
        with self.assertRaises(ValueError):
            self.provider.complete([], self.tools, model="qwen2.5:3b", tool_choice="required")

    def test_comparison_requires_both_assets_despite_scope_misclassification(self):
        self.route["in_scope"] = False
        self.provider._generate = Mock(side_effect=[
            (self.route, {}),
            ({"calls": [
                {"name": "inspect_device", "args": {"asset_id": "LT-901", "check": "hardware"}},
                {"name": "inspect_device", "args": {"asset_id": "DT-902", "check": "hardware"}},
            ], "reply": ""}, {}),
        ])
        result = self.complete("Compare hardware snapshots of LT-901 and DT-902")
        self.assertEqual(result.raw["route"]["mode"], "tools")
        schema = self.provider._generate.call_args_list[1].args[1]
        self.assertEqual(schema["properties"]["calls"]["minItems"], 2)

    def test_report_title_is_literal_and_report_only(self):
        self.tools.append({"type": "function", "function": {
            "name": "format_incident_report", "parameters": {
                "type": "object", "properties": {}, "required": ["findings", "template"],
            },
        }})
        self.provider._generate = Mock(side_effect=[
            (self.route, {}),
            ({"calls": [{"name": "format_incident_report", "args": {
                "incident_title": "Camera Case", "template": "technical", "findings": [],
            }}], "reply": ""}, {}),
        ])
        self.complete("Format findings into a technical report named 'Camera Case'")
        schema = self.provider._generate.call_args_list[1].args[1]
        variants = schema["properties"]["calls"]["items"]["anyOf"]
        self.assertEqual(len(variants), 1)
        self.assertEqual(variants[0]["properties"]["args"]["properties"]["incident_title"], {"const": "Camera Case"})

    def test_capability_question_does_not_search(self):
        self.provider._generate = Mock(return_value=(self.route, {}))
        self.assertEqual(self.complete("What can you help with?").tool_calls, [])
        self.assertEqual(self.provider._generate.call_count, 1)

    def test_application_generation_is_out_of_scope(self):
        self.provider._generate = Mock(return_value=(self.route, {}))
        result = self.complete("Build a Python application")
        self.assertEqual(result.tool_calls, [])
        self.assertTrue(result.text)


if __name__ == "__main__":
    unittest.main()
