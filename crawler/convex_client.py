import json
import os
import subprocess
from typing import Any, Optional

from dotenv import load_dotenv


def _load_env_files() -> None:
    """Load .env.local from the project root or the current package."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)

    candidates = [
        os.path.join(root_dir, ".env"),
        os.path.join(current_dir, ".env"),
        os.path.join(root_dir, ".env.local"),
        os.path.join(current_dir, ".env.local"),
    ]
    for env_file in candidates[:2]:
        if os.path.isfile(env_file):
            load_dotenv(env_file, override=False)
    for env_file in candidates[2:]:
        if os.path.isfile(env_file):
            load_dotenv(env_file, override=True)


def _convex_deployment() -> Optional[str]:
    return os.getenv("CONVEX_DEPLOYMENT")


def _convex_deploy_key() -> Optional[str]:
    """Return the full Convex deploy key from environment variables."""
    return os.getenv("CONVEX_DEPLOY_KEY") or os.getenv("CONVEX_ADMIN_KEY")


def _has_convex_config() -> bool:
    _load_env_files()
    return bool(_convex_deployment() or _convex_deploy_key())


def _run_convex_function(path: str, args: dict[str, Any]) -> Any:
    _load_env_files()

    if not _has_convex_config():
        raise RuntimeError(
            "Convex is not configured. Set CONVEX_DEPLOYMENT or "
            "CONVEX_DEPLOY_KEY in your .env.local file."
        )

    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    cli_path = os.path.join(root_dir, "node_modules", "convex", "bin", "main.js")
    if not os.path.isfile(cli_path):
        raise RuntimeError(f"Convex CLI not found at {cli_path}")

    command = [
        "node",
        "--use-system-ca",
        cli_path,
        "run",
        path,
        json.dumps(args, separators=(",", ":")),
        "--typecheck",
        "disable",
        "--codegen",
        "disable",
    ]
    try:
        result = subprocess.run(
            command,
            cwd=root_dir,
            env=os.environ.copy(),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError as exc:
        raise RuntimeError(f"Unable to run the Convex CLI: {exc}") from exc

    if result.returncode != 0:
        output = "\n".join(
            part.strip() for part in (result.stdout, result.stderr) if part and part.strip()
        )
        raise RuntimeError(f"Convex function {path} failed: {output}")

    output = result.stdout.strip()
    if not output:
        return None

    try:
        return json.loads(output)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Convex function {path} returned invalid CLI output: {output}"
        ) from exc


def call_mutation(
    path: str,
    args: dict[str, Any],
    *,
    url: Optional[str] = None,
    deploy_key: Optional[str] = None,
) -> Any:
    """Run a Convex mutation through the CLI so internal mutations are supported."""
    del url, deploy_key
    return _run_convex_function(path, args)


def call_query(
    path: str,
    args: dict[str, Any],
    *,
    url: Optional[str] = None,
    deploy_key: Optional[str] = None,
) -> Any:
    del url, deploy_key
    return _run_convex_function(path, args)


def _push(function_path: str, args: dict[str, Any]) -> Any:
    return call_mutation(function_path, args)


def push_resort_hours(
    resort_id: str,
    source_url: str,
    hours: list[dict[str, Any]],
    *,
    function_path: str = "resortHours:save",
    updated_at_ms: Optional[int] = None,
) -> Any:
    args = {
        "resortId": resort_id,
        "sourceUrl": source_url,
        "hours": hours,
    }
    if updated_at_ms is not None:
        args["updatedAt"] = updated_at_ms

    return _push(function_path, args)


def push_resort_rates(
    resort_id: str,
    source_url: str,
    rates: Any,
    *,
    function_path: str = "resortRates:save",
    updated_at_ms: Optional[int] = None,
) -> Any:
    args = {
        "resortId": resort_id,
        "sourceUrl": source_url,
        "rates": rates,
    }
    if updated_at_ms is not None:
        args["updatedAt"] = updated_at_ms

    return _push(function_path, args)


def push_resort_rentals(
    resort_id: str,
    source_url: str,
    rentals: Any,
    *,
    function_path: str = "resortRentals:save",
    updated_at_ms: Optional[int] = None,
) -> Any:
    args = {
        "resortId": resort_id,
        "sourceUrl": source_url,
        "rentals": rentals,
    }
    if updated_at_ms is not None:
        args["updatedAt"] = updated_at_ms

    return _push(function_path, args)


def push_weather_and_status(
    resort_id: str,
    source_url: str,
    weather_data: dict[str, Any],
    *,
    function_path: str = "weatherAndStatus:save",
    updated_at_ms: Optional[int] = None,
) -> Any:
    args = {
        "resortId": resort_id,
        "sourceUrl": source_url,
        **weather_data,
    }
    if updated_at_ms is not None:
        args["updatedAt"] = updated_at_ms

    return _push(function_path, args)


def push_ski_resorts(
    records: list[dict[str, Any]],
    *,
    function_path: str = "resorts:saveMany",
    batch_size: int = 100,
) -> Any:
    results = []
    for start in range(0, len(records), batch_size):
        batch = records[start : start + batch_size]
        result = _push(function_path, {"resorts": batch})
        if result is None:
            return None
        results.extend(result)
        print(f"Pushed {min(start + batch_size, len(records))}/{len(records)} records to Convex")

    return results


def push_locations(
    locations: list[dict[str, str]],
    *,
    function_path: str = "locations:sync",
) -> Any:
    return _push(function_path, {"locations": locations})
