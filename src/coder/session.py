"""Persistent state and sandbox lifecycle for resumable coding sessions."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from coder.tools.sandbox_tools import SANDBOX_DIR


STATE_FILE = Path(__file__).parents[2] / "output" / ".coder_session.json"


@dataclass
class CodingSession:
    assignment: str
    last_error: str = ""
    resume_requested: bool = False


def load_session() -> CodingSession | None:
    """Load the last valid session, if one exists."""
    try:
        payload = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        assignment = payload["assignment"].strip()
        if not assignment:
            return None
        return CodingSession(
            assignment=assignment,
            last_error=str(payload.get("last_error", "")),
        )
    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError, AttributeError):
        return None


def save_session(session: CodingSession) -> None:
    """Persist enough context for a later agent run to continue the program."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(
        json.dumps(
            {"assignment": session.assignment, "last_error": session.last_error},
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )


def has_resumable_session() -> bool:
    """Return whether both an assignment and generated sandbox files exist."""
    session = load_session()
    return session is not None and any(path.is_file() for path in SANDBOX_DIR.rglob("*"))


def reset_sandbox() -> None:
    """Remove generated files before starting a different program."""
    SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
    for path in SANDBOX_DIR.iterdir():
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def continuation_instructions(session: CodingSession) -> str:
    """Build explicit context that makes the agent repair existing work."""
    instructions = (
        "This is a continuation of the previous run. Inspect every existing file in "
        "the sandbox before editing. Preserve working functionality, finish incomplete "
        "requirements, run the program and its tests, and fix the actual causes of any "
        "failures instead of starting over."
    )
    if session.last_error:
        instructions += f" The previous run stopped with this error: {session.last_error}"
    return instructions
