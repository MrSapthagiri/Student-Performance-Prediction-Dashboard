import os
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

def main() -> None:
    print("Starting Student Performance Prediction Stack...")
    print("- Backend: http://127.0.0.1:5000")
    print("- Dashboard (New UI): http://localhost:8000")

    backend = subprocess.Popen(
        [sys.executable, str(ROOT_DIR / "backend" / "app.py")],
        cwd=str(ROOT_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    dashboard = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8000"],
        cwd=str(ROOT_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        backend.wait()
        dashboard.wait()
    except KeyboardInterrupt:
        backend.terminate()
        dashboard.terminate()


if __name__ == "__main__":
    main()
