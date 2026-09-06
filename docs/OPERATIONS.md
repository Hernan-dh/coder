# Operations

## Local setup

1. Install Python 3.10–3.13 and `uv`.
2. Run `uv sync`.
3. Copy `.env.example` to `.env` and set local credentials.
4. Run `uv run crewai run`.

The command presents exactly five curated coding projects. Enter `1` through
`5`, or enter `0` to provide a custom assignment. If generated files and saved
session metadata exist, option `6` resumes the previous program. Invalid and
empty custom selections are rejected before the crew starts.

Configure at least one of `GEMINI_API_KEY`, `GROQ_API_KEY`, or
`OPENROUTER_API_KEY`. Runtime model order is defined in
`src/coder/model_config.py`; free tiers remain subject to provider quotas.
Empty model responses automatically advance to the next configured provider.
Gemini is accessed through CrewAI's native Google Gen AI integration because
Gemini 3 tool calls require thought signatures to be retained across turns.
CLI output is forced to UTF-8 on Windows so CrewAI status symbols do not trigger
`charmap` encoding errors.

`SERPER_API_KEY` is optional. The coding agent uses Serper for current
documentation when configured, and DDGS otherwise. The generated program
still runs in the network-disabled Docker sandbox.

Generated files in `output/` and `sandbox*/` are local artifacts and are excluded from publication.

## Docker sandbox

Docker Desktop must be running with Linux containers enabled. The coder writes
generated files under `sandbox/` and runs Python files in disposable
`python:3.13-slim` containers. The runtime has no network, uses a read-only root
filesystem, and is limited to one CPU, 256 MB RAM, 64 processes, and 60 seconds.

Pull the runtime image once and run the local smoke test with:

```powershell
docker pull python:3.13-slim
uv run python -m unittest discover -s tests
```

If a run fails, confirm `docker version` shows both Client and Server. Sandbox
programs cannot download packages or contact external services by design.
The CLI also displays the failure and asks whether the coding agent should
resume immediately. Answer `y` to keep the sandbox, pass the error back to a
fresh CrewAI execution, and have the agent inspect and repair its program.
Answering no preserves the files and session metadata for option `6` on the
next invocation.

## Verification

Run `./scripts/verify.sh`, or on Windows run `uv run python scripts/verify.py`.
The verifier prepends the repository's `src` directory to the test process so
local package imports do not depend on whichever virtual environment is active.

Enable the repository-managed pre-commit hook once per clone with `uv run python scripts/install_hooks.py`. GitHub Actions runs the same verifier.

## Documentation

- Rebuild the changelog: `uv run python scripts/document.py changelog`.
- Create an ADR draft: `uv run python scripts/document.py decision "Decision title"`.

## Publishing

Preview a proposal with `uv run python scripts/publish.py --preview`. Interactive publication verifies the repository, proposes an English Conventional Commit title through Gemini with Groq fallback, and requires typing `PUBLISH` before staging, committing, and pushing.

Provide `--title` and `--description` to avoid external metadata generation. Commits and pushes always require explicit user authorization.

## Recovery

- If verification fails, fix every reported item and rerun it.
- If a coding run fails, answer `y` at the recovery prompt or restart the CLI
  and select `6`; neither path recreates the program from scratch.
- If metadata generation fails, inspect the provider attempt names, verify local keys and quotas, or provide commit metadata manually.
- Never recover with a force-push.

## Public-source verification

See [README](../README.md) for the reproducible setup. CI installs dependencies before invoking the verifier. Tests disable dotenv loading and provider telemetry and use synthetic inputs or mocked external calls; passing unit tests does not certify live services or production security.

The verifier invokes tests through uv in this repository so imports resolve even when verification is started from global Python. uv must be on PATH; use uv sync --locked for the committed dependency resolution.


## Publication review

Before publishing, run the verifier and review git diff and git status --short,
especially new files. Keep real credentials in local environment files or hosting
secrets, and preserve upstream license notices. Automated secret checks cover
recognizable patterns in current source files; they do not certify the absence of
secrets or scan every historical commit, remote ref, hosting log or fork. Removing
a file from the working tree does not remove it from Git history.
