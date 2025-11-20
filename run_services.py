"""Helper script to start backend, AI, and frontend services from the current terminal.

The previous iteration popped open the macOS Terminal app via AppleScript, which
isn't ideal when you're already inside VS Code/Cursor. This version keeps every
process attached to the invoking shell while still activating the local
virtualenv before launching each service.
"""
from __future__ import annotations

import platform
import shlex
import signal
import subprocess
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
VENV_ACTIVATE = PROJECT_ROOT / ".venv" / "bin" / "activate"


def _ensure_posix_shell(shell_path: str) -> None:
    """Ensure we're on a system where the requested shell exists."""
    if platform.system() == "Windows":
        raise OSError("run_services.py currently supports POSIX shells only (macOS/Linux).")
    if not Path(shell_path).exists():
        raise FileNotFoundError(f"Could not find shell at {shell_path}")


def _build_shell_command(user_command: str) -> str:
    """Compose the shell command that activates the venv before running user_command."""
    if not VENV_ACTIVATE.exists():
        raise FileNotFoundError(
            f"Could not find virtual environment activation script at {VENV_ACTIVATE}"
        )

    parts = [
        f"cd {shlex.quote(str(PROJECT_ROOT))}",
        f"source {shlex.quote(str(VENV_ACTIVATE))}",
        user_command,
    ]
    return " && ".join(parts)


def _spawn_service(label: str, user_command: str, shell_path: str) -> subprocess.Popen:
    """Launch a service in the background using the provided shell."""
    shell_command = _build_shell_command(user_command)
    print(f"Launching {label}: {shell_command}")
    return subprocess.Popen(
        [shell_path, "-c", shell_command],
        cwd=PROJECT_ROOT,
    )


def main() -> None:
    shell_path = "/bin/zsh" if Path("/bin/zsh").exists() else "/bin/bash"
    _ensure_posix_shell(shell_path)

    service_commands = [
        ("Backend", "python main.py"),
        ("AI", "cd ai && ./run.sh"),
        ("Frontend", "cd frontend && npm run dev"),
    ]

    processes: list[tuple[str, subprocess.Popen]] = []

    try:
        for label, user_command in service_commands:
            proc = _spawn_service(label, user_command, shell_path)
            processes.append((label, proc))

        print("All services launched. Press Ctrl+C to stop them.")

        while True:
            for label, proc in list(processes):
                if proc.poll() is not None:
                    raise RuntimeError(f"{label} exited with code {proc.returncode}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping services...")
    finally:
        for label, proc in processes:
            if proc.poll() is None:
                proc.send_signal(signal.SIGTERM)
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
        print("All services stopped.")


if __name__ == "__main__":
    main()