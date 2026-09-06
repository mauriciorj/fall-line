import subprocess
import sys
from datetime import datetime
from pathlib import Path


MY_TEST_DIR = Path(__file__).resolve().parent
FAILURE_LOG = MY_TEST_DIR / "crawler-errors.log"
RESORT_SCRIPTS = {
    "skisnowvalley": (
        "hours-of-operation.py",
        "lift-rates.py",
        "rentals.py",
        "weather-and-status.py",
        "push-existing-hours.py",
    ),
    # ERROR
    # "bluemountain": (
        # "hours-of-operation.py",
        # "lift-rates.py",
        # "rentals.py",
        # "weather-and-status.py",
    # ),
    "brimacombe": (
        "hours-of-operation.py",
        "lift-rates.py",
        "rentals.py",
        "weather-and-status.py",
    ),
    "caledon": (
        "lift-rates.py",
        "rentals.py",
        "weather-and-status.py",
    ),
    "chicopee": (
        "hours-of-operation.py",
        "rates.py",
        "rentals.py",
        "weather-and-status.py",
    ),
    "gleneden": (
        "lift-rates.py",
        "rentals.py",
        "weather-and-status.py",
    ),
    "horseshoeresort": (
        "lift-rates.py",
        "rentals.py",
        "weather-and-status.py",
    ),
    "ski-lakeridge": (
        "hours-of-operation.py",
        "lift-rates.py",
        "rentals.py",
        "weather-and-status.py",
    ),
    "skidagmar": (
        "hours-of-operation.py",
        "lift-rates.py",
        "rentals.py",
        "weather-and-status.py",
    ),
}


def run_script(resort_name, script_name):
    script_path = MY_TEST_DIR / resort_name / script_name
    command = [sys.executable, str(script_path)]

    print(f"\n=== Running {resort_name}/{script_name} ===", flush=True)
    result = subprocess.run(
        command,
        cwd=MY_TEST_DIR,
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
        log.write(f"\n[{timestamp}] Crawler failures\n")
        for resort_name, script_name, result in failures:
            log.write(f"\nResort: {resort_name}\n")
            log.write(f"Script: {script_name}\n")
            log.write(f"Exit code: {result.returncode}\n")
            log.write("--- stdout ---\n")
            log.write(result.stdout or "")
            log.write("\n--- stderr ---\n")
            log.write(result.stderr or "")
            log.write("\n")


def main():
    failures = []
    total_scripts = sum(len(scripts) for scripts in RESORT_SCRIPTS.values())

    for resort_name, scripts in RESORT_SCRIPTS.items():
        for script_name in scripts:
            result = run_script(resort_name, script_name)
            if result.returncode != 0:
                failures.append((resort_name, script_name, result))

    if failures:
        write_failure_log(failures)
        print(f"\nFailed scripts logged to {FAILURE_LOG}", file=sys.stderr)
        return 1

    print(f"\nAll {total_scripts} crawler scripts completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
