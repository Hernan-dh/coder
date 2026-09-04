# Architecture

## Purpose

`coder` is a CrewAI project whose agents and tasks are configured in YAML and orchestrated from Python.

## Components

- `src/coder/config/agents.yaml`: agent roles, goals, and backstories.
- `src/coder/config/tasks.yaml`: task descriptions and expected outputs.
- `src/coder/crew.py`: CrewAI agent, task, and crew construction.
- `src/coder/main.py`: command-line entry points and kickoff inputs.
- `src/coder/model_config.py`: version-controlled Gemini, Groq, and OpenRouter fallback order.
- `src/coder/model_provider.py`: per-call provider failover used by the CrewAI agent.
- `knowledge/`: versioned knowledge supplied to the crew.
- `output/` and `sandbox*/`: generated execution artifacts excluded from Git.
- `scripts/`: shared verification, documentation, hook installation, and safe publishing commands.

## Trust boundaries

- Prompts, model responses, tool results, generated code, and generated reports are untrusted.
- Credentials are loaded from the environment and must not enter Git, prompts, logs, or documentation.
- CrewAI model and tool providers are external services.

## Model routing

The coding agent receives one `FallbackLLM` instance. Each failed call advances
through configured providers without restarting completed CrewAI work: Gemini
Flash, Groq GPT-OSS, then coding-oriented and general agentic free OpenRouter
models. Providers without a configured key are omitted at startup.

## Related decisions

- [Continuous documentation and safe publishing](decisions/0001-continuous-documentation-and-safe-publishing.md)
