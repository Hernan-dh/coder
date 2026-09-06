# Coder

A command-line coding assistant that turns a requested Python program into files, runs them in a constrained Docker workspace, and can resume an interrupted assignment.

## Attribution

Project built from [Ed Donner's agentic AI engineering course](https://github.com/ed-donner/agents). The upstream MIT copyright notice is preserved in [LICENSE](LICENSE). No endorsement by the course author is implied.

## Run locally

Python 3.12 and uv are the documented development baseline. Docker is required for actual code generation, but not for unit tests. Run the following commands from this repository's root.

```sh
uv sync
```

Copy `.env.example` to `.env` (`Copy-Item .env.example .env` in PowerShell, or `cp .env.example .env` on Linux/macOS), then replace only the placeholders for the providers you intend to use. Leave unused credentials empty. Never commit the real `.env`.

Configure at least one model-provider key. Install and start Docker, then run `docker pull python:3.13-slim`. Select a preset or custom assignment in the CLI; existing sessions can be resumed.

```sh
uv run crewai run
```

## Architecture

```text
CLI assignment -> CrewAI coding agent -> constrained file tools -> network-disabled Docker -> results / resumable session
```

See [architecture](docs/ARCHITECTURE.md) for components, data flow and trust boundaries, and [operations](docs/OPERATIONS.md) for configuration and recovery.

## Technologies

Python, CrewAI, YAML, Docker, unittest and uv; Gemini, Groq and OpenRouter model providers.

## Reproducible tests

After installing the dependencies above:

```sh
uv run python -m unittest discover -v
uv run python scripts/verify.py
```

Coverage: Provider failover, rejected empty outputs, tool schemas, sandbox boundaries and resumable sessions; Docker and providers are mocked. Tests run without real credentials or paid API calls. They do not measure model quality, live provider availability, or full browser behavior. CI installs dependencies and runs the same verifier on pushes and pull requests.

## Limitations

Generated programs need human review. Docker limits reduce exposure but are not a security certification. Runtime containers have no network and cannot freely install dependencies. Starting a new assignment resets generated sandbox files. Model availability, tool-call quality and quotas can interrupt work.

Prompts and relevant context are sent to external model/search providers. Do not submit secrets or confidential data. Provider names in source code are configuration, not promises of current availability, pricing, or free access.

## Public repository and license

The repository includes a placeholder-only [.env.example](.env.example); local credentials, caches and generated artifacts are excluded by [.gitignore](.gitignore). See [operations](docs/OPERATIONS.md) for verification and publication instructions.

The code is distributed under the [MIT license](LICENSE). Dependencies retain their own licenses. Biographical material, third-party documents, logos and linked content are not relicensed by this code license. Publishing scripts can send code diffs to external models when generating commit text; use explicit metadata to avoid that step.
