import subprocess
import sys
from datetime import datetime
from pathlib import Path


MOUNTAINS_DIR = Path(__file__).resolve().parent
CRAWLER_DIR = MOUNTAINS_DIR.parent
FAILURE_LOG = CRAWLER_DIR / "crawler-errors.log"
RESORT_MAIN_FILES = tuple(sorted(path for path in MOUNTAINS_DIR.rglob("main.py") if path.parent != MOUNTAINS_DIR))


def run_main(script_path):
    print(f"\n=== Running {script_path.parent.name}/main.py ===", flush=True)
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=script_path.parent,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)

    return result


def write_failure_log(failures):
    timestamp = datetime.now().astimezone().isoformat()
    with FAILURE_LOG.open("a", encoding="utf-8") as log:
        log.write(f"\n[{timestamp}] Mountain main failures\n")
        for script_path, result in failures:
            log.write(f"\nResort: {script_path.parent.name}\n")
            log.write(f"Script: {script_path.name}\n")
            log.write(f"Exit code: {result.returncode}\n")
            log.write("--- stdout ---\n")
            log.write(result.stdout or "")
            log.write("\n--- stderr ---\n")
            log.write(result.stderr or "")
            log.write("\n")


def main():
    failures = []

    for script_path in RESORT_MAIN_FILES:
        result = run_main(script_path)
        if result.returncode != 0:
            failures.append((script_path, result))

    if failures:
        write_failure_log(failures)
        print(f"\nFailed scripts logged to {FAILURE_LOG}", file=sys.stderr)
        return 1

    print(f"\nAll {len(RESORT_MAIN_FILES)} mountain main scripts completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
