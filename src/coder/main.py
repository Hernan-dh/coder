#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from coder.crew import Coder
from coder.model_provider import fallback_llm

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

CODING_OPTIONS = (
    "Create a command-line calculator with input validation and unit tests.",
    "Create a JSON-backed command-line to-do list with add, list, complete, and delete commands.",
    "Create a CSV analyzer that reports row counts, missing values, and numeric-column statistics.",
    "Create a personal expense tracker that stores entries in JSON and summarizes spending by category.",
    "Create a duplicate-file finder that compares file sizes and SHA-256 hashes without deleting files.",
    "Create a log-file analyzer that counts severity levels and reports the most frequent errors.",
    "Create a secure password generator using Python's secrets module and configurable character rules.",
    "Create a Markdown-to-HTML converter using only the Python standard library.",
    "Create a small JSON REST API using Python's standard-library HTTP server.",
    "Create a file-organizer preview tool that proposes moves by extension without modifying files.",
)


def prompt_assignment() -> str:
    """Offer ten coding projects or accept a custom assignment."""
    print("\nChoose a coding project:")
    for index, assignment in enumerate(CODING_OPTIONS, start=1):
        print(f"{index}. {assignment}")
    print("C. Write a custom assignment")

    while True:
        choice = input("\nChoose 1-10 or C: ").strip()
        if choice.lower() == "c":
            custom = input("Describe the coding task:\n> ").strip()
            if custom:
                return custom
            print("The custom assignment cannot be empty.")
            continue
        try:
            option = int(choice)
        except ValueError:
            option = 0
        if 1 <= option <= len(CODING_OPTIONS):
            return CODING_OPTIONS[option - 1]
        print("Invalid choice. Enter a number from 1 to 10, or C.")

def run():
    """
    Run the crew.
    """
    inputs = {
        'assignment': prompt_assignment()
    }

    try:
        Coder(llm=fallback_llm()).crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


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
