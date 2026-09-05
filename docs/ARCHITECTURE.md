# Architecture

## Purpose

`coder` is a CrewAI project whose agents and tasks are configured in YAML and orchestrated from Python.

## Components

- `src/coder/config/agents.yaml`: agent roles, goals, and backstories.
- `src/coder/config/tasks.yaml`: task descriptions and expected outputs.
- `src/coder/crew.py`: CrewAI agent, task, and crew construction.
- `src/coder/main.py`: command-line entry points and kickoff inputs.
- `src/coder/session.py`: persistent assignment/error metadata, fresh-sandbox
  setup, and continuation instructions for resumable runs.
- `src/coder/model_config.py`: version-controlled Gemini, Groq, and OpenRouter fallback order.
- `src/coder/model_provider.py`: per-call provider failover used by the CrewAI agent.
- `src/coder/tools/sandbox_tools.py`: constrained file operations and ephemeral
  Docker execution for generated Python programs.
- `knowledge/`: versioned knowledge supplied to the crew.
- `output/` and `sandbox*/`: generated execution artifacts excluded from Git.
- `scripts/`: shared verification, documentation, hook installation, and safe publishing commands.

## Trust boundaries

- Prompts, model responses, tool results, generated code, and generated reports are untrusted.
- Credentials are loaded from the environment and must not enter Git, prompts, logs, or documentation.
- CrewAI model and tool providers are external services.
- Generated Python executes in an ephemeral container with no network, a
  read-only root filesystem, dropped Linux capabilities, and bounded CPU,
  memory, process count, and execution time. Only `sandbox/` is bind-mounted
  read-write; tool paths are resolved and checked against that boundary.

## Resumable execution

The CLI stores the current assignment and last runtime error in the ignored
`output/.coder_session.json` file. A new project clears only generated sandbox
content. A resumed project retains it and starts a new CrewAI execution with
instructions to inspect, test, and repair those existing files. Runtime errors
offer this same continuation path without terminating the CLI process.

## Model routing

The coding agent receives one `FallbackLLM` instance. Each failed call advances
through configured providers without restarting completed CrewAI work. Gemini
uses CrewAI's native Google Gen AI provider so tool-call thought signatures are
preserved; Groq and OpenRouter use their OpenAI-compatible endpoints. Providers
without a configured key are omitted at startup. When execution changes from
Gemini to an OpenAI-compatible provider mid-task, Gemini-only message metadata
is removed while standard tool-call data is retained.
`None`, empty, and whitespace-only provider responses are treated as failed
calls, so routing reaches another configured model before CrewAI validates the
response.

## Related decisions

- [Continuous documentation and safe publishing](decisions/0001-continuous-documentation-and-safe-publishing.md)
