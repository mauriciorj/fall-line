import subprocess
import sys
from pathlib import Path

MOUNTAINS_DIR = Path(__file__).resolve().parent
SNAPSHOT_GENERATORS = tuple(sorted(path for path in MOUNTAINS_DIR.rglob("snapshot_generator.py") if path.parent != MOUNTAINS_DIR))


def run_snapshot_generator(script_path):
    print(f"\n=== Running {script_path.parent.name}/snapshot_generator.py ===", flush=True)
    return subprocess.run(
        [sys.executable, str(script_path)],
        cwd=script_path.parent,
        check=False,
    )


def main():
    failures = []

    for script_path in SNAPSHOT_GENERATORS:
        result = run_snapshot_generator(script_path)
        if result.returncode != 0:
            failures.append(script_path.parent.name)

    if failures:
        print(
            f"\nSnapshot generation failed for: {', '.join(failures)}",
            file=sys.stderr,
        )
        return 1

    print(
        f"\nAll {len(SNAPSHOT_GENERATORS)} snapshot generators completed successfully."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
