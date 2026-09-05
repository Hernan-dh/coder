from crewai.tools import tool
from pathlib import Path
import subprocess


SANDBOX_DIR = Path(__file__).parents[3] / "sandbox"
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
DOCKER_IMAGE = "python:3.13-slim"
EXECUTION_TIMEOUT_SECONDS = 60


def _sandbox_path(filename: str) -> Path:
    """Return a path contained by the sandbox, rejecting traversal attempts."""
    if not filename or Path(filename).is_absolute():
        raise ValueError("Use a non-empty path relative to the sandbox.")

    path = (SANDBOX_DIR / filename).resolve()
    try:
        path.relative_to(SANDBOX_DIR.resolve())
    except ValueError as exc:
        raise ValueError("The path must stay inside the sandbox.") from exc
    return path

@tool("List Sandbox Files")
def list_sandbox_files(directory: str = ".") -> str:
    """
    List the filenames currently in the sandbox directory.

    Args:
        directory: Reserved for schema compatibility; use "." for the sandbox root.

    Returns:
        A newline-separated list of filenames, or a message if the
        sandbox is empty.
    """
    try:
        root = _sandbox_path(directory)
    except ValueError as exc:
        return str(exc)
    if not root.is_dir():
        return f"No such directory in the sandbox: {directory}"
    names = sorted(str(p.relative_to(SANDBOX_DIR)) for p in root.iterdir())
    return "\n".join(names) if names else "The sandbox is empty."


@tool("Read Sandbox File")
def read_sandbox_file(filename: str) -> str:
    """
    Read and return the text contents of a file in the sandbox directory.

    Args:
        filename: The name of the file to read (e.g. "solution.py").
    Returns:
        The file's contents, or a message if the file does not exist.
    """
    try:
        path = _sandbox_path(filename)
    except ValueError as exc:
        return str(exc)
    if not path.is_file():
        return f"No such file in the sandbox: {filename}"
    return path.read_text()


@tool("Write Sandbox File")
def write_sandbox_file(filename: str, content: str) -> str:
    """
    Write text to a file in the sandbox directory, replacing any existing
    file with the same name.

    Args:
        filename: The name of the file to write (e.g. "solution.py").
        content: The text content to write.
    Returns:
        A confirmation message.
    """
    try:
        path = _sandbox_path(filename)
    except ValueError as exc:
        return str(exc)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return f"Wrote {len(content)} characters to {filename}."


@tool("Run Sandbox Python File")
def run_sandbox_python(filename: str) -> str:
    """
    Execute a Python file from the sandbox directory inside an ephemeral
    Docker container, with the sandbox mounted as the working directory,
    and return whatever the script printed to stdout.

    Args:
        filename: The name of the Python file to run (e.g. "solution.py").
    Returns:
        The text printed to stdout by the executed script.
    """
    try:
        path = _sandbox_path(filename)
    except ValueError as exc:
        return str(exc)
    if not path.is_file() or path.suffix.lower() != ".py":
        return f"No such Python file in the sandbox: {filename}"

    relative_filename = path.relative_to(SANDBOX_DIR).as_posix()
    command = [
        "docker", "run", "--rm",
        "--network", "none",
        "--memory", "256m",
        "--cpus", "1",
        "--pids-limit", "64",
        "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges",
        "--read-only",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m",
        "--volume", f"{SANDBOX_DIR}:/workspace:rw",
        "--workdir", "/workspace",
        DOCKER_IMAGE,
        "python", relative_filename,
    ]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=EXECUTION_TIMEOUT_SECONDS,
        )
    except FileNotFoundError:
        return "Docker is not installed or is not available on PATH."
    except subprocess.TimeoutExpired:
        return f"Execution stopped after {EXECUTION_TIMEOUT_SECONDS} seconds."

    output = result.stdout
    if result.stderr:
        output += ("\n" if output else "") + result.stderr
    return f"Exit code: {result.returncode}\n{output}".rstrip()

sandbox_tools = [list_sandbox_files, read_sandbox_file, write_sandbox_file, run_sandbox_python]


def _never_cache(*_args, **_kwargs) -> bool:
    return False


# Sandbox state changes between calls (files appear/change/run), so caching tool
# results would feed agents stale data. Opt out of CrewAI's default tool caching.
for _t in sandbox_tools:
    _t.cache_function = _never_cache
