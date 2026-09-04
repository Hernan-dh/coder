import os
import unittest
from unittest.mock import patch

from coder.model_config import MODEL_FALLBACKS
from coder.model_provider import fallback_llm


class ModelProviderTests(unittest.TestCase):
    def test_provider_order_starts_with_latest_gemini(self):
        self.assertEqual(MODEL_FALLBACKS[0].model, "gemini-3.8-flash")
        self.assertEqual(MODEL_FALLBACKS[2].model, "openai/gpt-oss-120b")
        self.assertEqual(MODEL_FALLBACKS[3].model, "cohere/north-mini-code:free")

    def test_requires_at_least_one_key(self):
        with patch.dict(os.environ, {
            "GEMINI_API_KEY": "",
            "GROQ_API_KEY": "",
            "OPENROUTER_API_KEY": "",
        }, clear=False):
            with self.assertRaisesRegex(RuntimeError, "Configure at least one provider key"):
                fallback_llm()


if __name__ == "__main__":
    unittest.main()
