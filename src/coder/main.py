#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from coder.crew import Coder
from coder.model_provider import fallback_llm
from coder.session import (
    CodingSession,
    continuation_instructions,
    has_resumable_session,
    load_session,
    reset_sandbox,
    save_session,
)

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

CODING_OPTIONS = (
    "Create a personal-finance CLI with budgets, recurring transactions, CSV import, and useful reports.",
    "Create a local Kanban project manager with JSON persistence, priorities, deadlines, and search.",
    "Create a log-analysis tool that detects recurring errors and produces a standalone HTML dashboard.",
    "Create an inventory and sales REST API with persistence, validation, reports, and automated tests.",
    "Create a duplicate-media organizer that hashes files and previews safe cleanup plans without deleting anything.",
)


def prompt_assignment(can_resume: bool | None = None) -> CodingSession:
    """Offer five curated projects, a custom assignment, and optional resume."""
    if can_resume is None:
        can_resume = has_resumable_session()

    print("\nChoose a coding project:")
    print("0. Describe your own program")
    for index, assignment in enumerate(CODING_OPTIONS, start=1):
        print(f"{index}. {assignment}")
    if can_resume:
        print("6. Resume the previous program")

    while True:
        available = "0-6" if can_resume else "0-5"
        choice = input(f"\nChoose {available}: ").strip()
        if choice == "0":
            custom = input("Describe the coding task:\n> ").strip()
            if custom:
                return CodingSession(custom)
            print("The custom assignment cannot be empty.")
            continue
        try:
            option = int(choice)
        except ValueError:
            option = -1
        if 1 <= option <= len(CODING_OPTIONS):
            return CodingSession(CODING_OPTIONS[option - 1])
        if option == 6 and can_resume:
            session = load_session()
            if session is not None:
                session.resume_requested = True
                return session
        print(f"Invalid choice. Enter a number from {available}.")


def _run_session(session: CodingSession, *, resume: bool) -> None:
    """Run or repeatedly resume a session without discarding generated files."""
    while True:
        save_session(session)
        run_assignment = session.assignment
        if resume:
            run_assignment = f"{run_assignment}\n\n{continuation_instructions(session)}"
        inputs = {"assignment": run_assignment}
        try:
            Coder(llm=fallback_llm()).crew().kickoff(inputs=inputs)
            session.last_error = ""
            save_session(session)
            return
        except Exception as error:
            session.last_error = f"{type(error).__name__}: {error}"
            save_session(session)
            print(f"\nCoder stopped with an error: {session.last_error}")
            answer = input("Resume the previous program from its existing files? [y/N]: ").strip().lower()
            if answer not in {"y", "yes"}:
                raise RuntimeError(f"Coder stopped: {error}") from error
            resume = True

def run():
    """
    Run the crew.
    """
    resumable_before_selection = has_resumable_session()
    session = prompt_assignment(resumable_before_selection)
    resume = session.resume_requested
    if not resume:
        reset_sandbox()
    _run_session(session, resume=resume)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        Coder(llm=fallback_llm()).crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Coder(llm=fallback_llm()).crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }

    try:
        Coder(llm=fallback_llm()).crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def run_with_trigger():
    """
    Run the crew with trigger payload.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "topic": "",
        "current_year": ""
    }

    try:
        result = Coder(llm=fallback_llm()).crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")
