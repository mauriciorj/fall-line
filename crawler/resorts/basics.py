import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

RESORTS_DIR = Path(__file__).resolve().parent
CRAWLER_DIR = RESORTS_DIR.parent
FAILURE_LOG = CRAWLER_DIR / "crawler-errors.log"
BASICS_FILE_NAME = "basics.py"


def list_children(directory):
    return sorted(
        path.name
        for path in directory.iterdir()
        if path.is_dir() and not path.name.startswith(("_", "."))
    )


def resolve_child(directory, name, label):
    available = list_children(directory)
    matches = [item for item in available if item.lower() == name.lower()]
    if not matches:
        raise SystemExit(
            f"Unknown {label} '{name}'. Available: {', '.join(available) or 'none'}"
        )
    return matches[0]


def resolve_scope(country, region):
    if region and not country:
        raise SystemExit("A region requires a country")

    scope = RESORTS_DIR
    if country:
        scope = scope / resolve_child(scope, country, "country")
    if region:
        scope = scope / resolve_child(scope, region, "region")
    return scope


def find_basics_files(scope):
    return sorted(
        path
        for path in scope.rglob(BASICS_FILE_NAME)
        if path.parent != RESORTS_DIR and "json_generators" not in path.parts
    )


def is_empty(script_path):
    return not script_path.read_text(encoding="utf-8").strip()


def resort_label(script_path):
    return "/".join(script_path.parent.relative_to(RESORTS_DIR).parts)


def run_basics(script_path):
    print(f"\n=== Running {resort_label(script_path)}/{BASICS_FILE_NAME} ===", flush=True)
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
        log.write(f"\n[{timestamp}] Resort basics failures\n")
        for script_path, result in failures:
            log.write(f"\nResort: {resort_label(script_path)}\n")
            log.write(f"Script: {script_path.name}\n")
            log.write(f"Exit code: {result.returncode}\n")
            log.write("--- stdout ---\n")
            log.write(result.stdout or "")
            log.write("\n--- stderr ---\n")
            log.write(result.stderr or "")
            log.write("\n")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run every resort basics.py (skiresort.json -> basics.json -> Convex)."
    )
    parser.add_argument("country", nargs="?", help="country folder, e.g. canada")
    parser.add_argument(
        "region",
        nargs="?",
        help="region folder inside the country, e.g. alberta (requires country)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="list the basics.py files that would run and exit",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    scope = resolve_scope(args.country, args.region)
    found = find_basics_files(scope)
    skipped = [path for path in found if is_empty(path)]
    scripts = [path for path in found if path not in skipped]
    for script_path in skipped:
        print(f"Skipped (empty {BASICS_FILE_NAME}): {resort_label(script_path)}")
    if not scripts:
        print(f"No runnable {BASICS_FILE_NAME} found under {scope}", file=sys.stderr)
        return 1

    if args.dry_run:
        for script_path in scripts:
            print(resort_label(script_path))
        print(f"\n{len(scripts)} {BASICS_FILE_NAME} file(s) would run, {len(skipped)} skipped.")
        return 0

    failures = []
    for script_path in scripts:
        result = run_basics(script_path)
        if result.returncode != 0:
            failures.append((script_path, result))

    if failures:
        write_failure_log(failures)
        print(f"\n{len(failures)}/{len(scripts)} failed:", file=sys.stderr)
        for script_path, _ in failures:
            print(f"  - {resort_label(script_path)}", file=sys.stderr)
        print(f"Failures logged to {FAILURE_LOG}", file=sys.stderr)
        return 1

    print(f"\nAll {len(scripts)} {BASICS_FILE_NAME} scripts completed successfully ({len(skipped)} skipped).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
