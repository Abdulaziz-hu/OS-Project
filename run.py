"""Create the project virtual environment, install requirements, and start the app."""

from pathlib import Path
import os
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parent
VENV_DIR = ROOT / ".venv"
REQUIREMENTS = ROOT / "requirements.txt"
APP = ROOT / "app.py"


def venv_python() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def main() -> int:
    if not VENV_DIR.exists():
        print("Creating virtual environment...")
        venv.EnvBuilder(with_pip=True).create(VENV_DIR)

    python = venv_python()
    if not python.exists():
        print("Could not find the Python executable inside .venv.", file=sys.stderr)
        return 1

    print("Installing requirements...")
    result = subprocess.run(
        [str(python), "-m", "pip", "install", "-r", str(REQUIREMENTS)],
        cwd=ROOT,
    )
    if result.returncode != 0:
        return result.returncode

    print("Starting OS Simulator...")
    return subprocess.run([str(python), str(APP)], cwd=ROOT).returncode


if __name__ == "__main__":
    raise SystemExit(main())
