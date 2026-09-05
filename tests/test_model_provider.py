import os
import unittest
from unittest.mock import MagicMock, patch

from crewai.llms.base_llm import BaseLLM

from coder.main import CODING_OPTIONS, _run_session, prompt_assignment
from coder.model_config import MODEL_FALLBACKS
from coder.model_provider import FallbackLLM, fallback_llm, openai_compatible_messages
from coder.tools.sandbox_tools import (
    list_sandbox_files,
    read_sandbox_file,
    run_sandbox_python,
    write_sandbox_file,
)
from coder.session import CodingSession, continuation_instructions


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

    def test_empty_response_advances_to_next_provider(self):
        first = MagicMock(spec=BaseLLM)
        second = MagicMock(spec=BaseLLM)
        first.call.return_value = "   "
        second.call.return_value = "usable response"
        llm = FallbackLLM(
            model="test-fallback",
            attempts=[
                (MODEL_FALLBACKS[0], first),
                (MODEL_FALLBACKS[1], second),
            ],
        )

        result = llm.call("continue")

        self.assertEqual(result, "usable response")
        self.assertEqual(llm.active_index, 1)
        first.call.assert_called_once()
        second.call.assert_called_once()

    def test_all_empty_responses_report_fallback_failure(self):
        provider = MagicMock(spec=BaseLLM)
        provider.call.return_value = None
        llm = FallbackLLM(
            model="test-fallback",
            attempts=[(MODEL_FALLBACKS[0], provider)],
        )

        with self.assertRaisesRegex(RuntimeError, "All configured models failed"):
            llm.call("continue")


class AssignmentPromptTests(unittest.TestCase):
    def test_offers_exactly_five_curated_assignments(self):
        self.assertEqual(len(CODING_OPTIONS), 5)

    @patch("builtins.input", return_value="4")
    def test_uses_numbered_assignment(self, _input):
        self.assertEqual(prompt_assignment(can_resume=False).assignment, CODING_OPTIONS[3])

    @patch("builtins.input", side_effect=["0", "Create a command-line calculator"])
    def test_accepts_custom_assignment(self, _input):
        self.assertEqual(
            prompt_assignment(can_resume=False).assignment,
            "Create a command-line calculator",
        )

    @patch("builtins.input", side_effect=["11", "c", "2"])
    def test_reprompts_after_invalid_number(self, _input):
        self.assertEqual(prompt_assignment(can_resume=False).assignment, CODING_OPTIONS[1])

    @patch("coder.main.load_session", return_value=CodingSession("Previous program", "failure"))
    @patch("builtins.input", return_value="6")
    def test_resumes_previous_assignment(self, _input, _load):
        session = prompt_assignment(can_resume=True)
        self.assertEqual(session.assignment, "Previous program")
        self.assertEqual(session.last_error, "failure")
        self.assertTrue(session.resume_requested)

    def test_continuation_includes_previous_failure(self):
        instructions = continuation_instructions(CodingSession("Program", "two tests failed"))
        self.assertIn("existing file", instructions)
        self.assertIn("two tests failed", instructions)

    @patch("coder.main.save_session")
    @patch("coder.main.fallback_llm", return_value=object())
    @patch("coder.main.Coder")
    @patch("builtins.input", return_value="y")
    def test_failure_can_resume_without_restarting(self, _input, coder, _llm, save):
        kickoff = coder.return_value.crew.return_value.kickoff
        kickoff.side_effect = [ValueError("tests failed"), None]
        session = CodingSession("Build it")

        _run_session(session, resume=False)

        self.assertEqual(kickoff.call_count, 2)
        second_inputs = kickoff.call_args_list[1].kwargs["inputs"]
        self.assertIn("tests failed", second_inputs["assignment"])
        self.assertGreaterEqual(save.call_count, 3)


class SandboxToolTests(unittest.TestCase):
    def test_rejects_paths_outside_sandbox(self):
        self.assertIn("inside the sandbox", read_sandbox_file.run("../.env"))
        self.assertIn("inside the sandbox", write_sandbox_file.run("../escape.py", ""))
        self.assertIn("inside the sandbox", run_sandbox_python.run("../escape.py"))

    @patch("coder.tools.sandbox_tools.subprocess.run")
    def test_runs_python_with_docker_isolation(self, run):
        write_sandbox_file.run("test_script.py", "print('ok')")
        run.return_value.returncode = 0
        run.return_value.stdout = "ok\n"
        run.return_value.stderr = ""

        result = run_sandbox_python.run("test_script.py")

        command = run.call_args.args[0]
        self.assertIn("none", command)
        self.assertIn("256m", command)
        self.assertIn("no-new-privileges", command)
        self.assertIn("--read-only", command)
        self.assertEqual(result, "Exit code: 0\nok")


if __name__ == "__main__":
    unittest.main()
