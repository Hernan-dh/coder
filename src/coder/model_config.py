"""Version-controlled runtime model order for the coding crew."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelSpec:
    label: str
    model: str
    api_key_env: str
    base_url: str


GEMINI_API_KEY_ENVIRONMENTS = ("GEMINI_API_KEY", "GEMINI_API_KEY_2", "GEMINI_API_KEY_3", "GEMINI_API_KEY_4")
GEMINI_MODELS = ("gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash")

MODEL_FALLBACKS = (
    *(ModelSpec("Gemini", model, key_env, "https://generativelanguage.googleapis.com/v1beta/openai/") for key_env in GEMINI_API_KEY_ENVIRONMENTS for model in GEMINI_MODELS),
    ModelSpec("Groq", "openai/gpt-oss-120b", "GROQ_API_KEY", "https://api.groq.com/openai/v1"),
    ModelSpec("Groq", "qwen/qwen3.8-27b", "GROQ_API_KEY", "https://api.groq.com/openai/v1"),
    ModelSpec("OpenRouter", "cohere/north-mini-code:free", "OPENROUTER_API_KEY", "https://openrouter.ai/api/v1"),
    ModelSpec("OpenRouter", "nvidia/nemotron-3-ultra-550b-a55b:free", "OPENROUTER_API_KEY", "https://openrouter.ai/api/v1"),
)

MODEL_TIMEOUT_SECONDS = 90
MODEL_MAX_OUTPUT_TOKENS = 16_384
