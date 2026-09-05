import os
import unittest
from unittest.mock import patch

from coder.main import CODING_OPTIONS, prompt_assignment
from coder.model_config import MODEL_FALLBACKS
from coder.model_provider import fallback_llm, openai_compatible_messages
from coder.tools.sandbox_tools import list_sandbox_files


class ModelProviderTests(unittest.TestCase):
    def test_provider_order_starts_with_latest_gemini(self):
        self.assertEqual(MODEL_FALLBACKS[0].model, "gemini-3.8-flash")
        models = [spec.model for spec in MODEL_FALLBACKS]
        self.assertIn("gemini-3.6-flash", models)
        self.assertIn("openai/gpt-oss-120b", models)
        self.assertIn("qwen/qwen3.8-27b", models)
        self.assertIn("cohere/north-mini-code:free", models)

    def test_requires_at_least_one_key(self):
        with patch.dict(os.environ, {
            "GEMINI_API_KEY": "",
            "GROQ_API_KEY": "",
            "OPENROUTER_API_KEY": "",
        }, clear=False):
            with self.assertRaisesRegex(RuntimeError, "Configure at least one provider key"):
                fallback_llm()

    def test_no_argument_tool_has_object_properties_for_groq(self):
        schema = list_sandbox_files.args_schema.model_json_schema()
        self.assertEqual(schema["type"], "object")
        self.assertIn("directory", schema["properties"])

    def test_removes_gemini_metadata_before_cross_provider_fallback(self):
        messages = [{
            "role": "assistant",
            "content": "",
            "tool_calls": [{"id": "call-1"}],
            "raw_tool_call_parts": [{"thought_signature": "opaque"}],
        }]
        cleaned = openai_compatible_messages(messages)  # type: ignore[arg-type]
        self.assertNotIn("raw_tool_call_parts", cleaned[0])
        self.assertEqual(cleaned[0]["tool_calls"], [{"id": "call-1"}])


class AssignmentPromptTests(unittest.TestCase):
    @patch("builtins.input", return_value="4")
    def test_uses_numbered_assignment(self, _input):
        self.assertEqual(prompt_assignment(), CODING_OPTIONS[3])

    @patch("builtins.input", side_effect=["c", "Create a command-line calculator"])
    def test_accepts_custom_assignment(self, _input):
        self.assertEqual(prompt_assignment(), "Create a command-line calculator")

    @patch("builtins.input", side_effect=["11", "0", "2"])
    def test_reprompts_after_invalid_number(self, _input):
        self.assertEqual(prompt_assignment(), CODING_OPTIONS[1])


if __name__ == "__main__":
    unittest.main()
