import json
import os
from typing import Any, Optional

import truststore

truststore.inject_into_ssl()

import requests
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


def _convex_url() -> Optional[str]:
    """Return the Convex deployment URL from environment variables."""
    return os.getenv("CONVEX_URL") or os.getenv("NEXT_PUBLIC_CONVEX_URL")


def _convex_deploy_key() -> Optional[str]:
    """Return the full Convex deploy key from environment variables."""
    return os.getenv("CONVEX_DEPLOY_KEY") or os.getenv("CONVEX_ADMIN_KEY")


def _has_convex_config() -> bool:
    _load_env_files()
    return bool(_convex_url() and _convex_deploy_key())


def call_mutation(
    path: str,
    args: dict[str, Any],
    *,
    url: Optional[str] = None,
    deploy_key: Optional[str] = None,
) -> Any:
    """Call a Convex mutation over the HTTP API using a deploy key."""
    _load_env_files()

    convex_url = url or _convex_url()
    key = deploy_key or _convex_deploy_key()

    if not convex_url or not key:
        raise RuntimeError(
            "Convex URL and deploy key are not configured. "
            "Set CONVEX_URL (or NEXT_PUBLIC_CONVEX_URL) and CONVEX_DEPLOY_KEY "
            "(or CONVEX_ADMIN_KEY) in your .env.local file."
        )

    body = {
        "path": path,
        "args": args,
        "format": "json",
    }

    ca_bundle = os.getenv("REQUESTS_CA_BUNDLE") or os.getenv("CURL_CA_BUNDLE")

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Convex {key}",
    }

    response = requests.post(
        f"{convex_url.rstrip('/')}/api/mutation",
        headers=headers,
        json=body,
        verify=ca_bundle if ca_bundle else True,
    )

    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        # Do not include the Authorization value in any logged error.
        message = (
            f"Convex mutation {path} failed: {exc.response.status_code} "
            f"{exc.response.reason}: {exc.response.text}"
        )
        raise RuntimeError(message) from exc

    payload = response.json()
    if payload.get("status") == "success":
        return payload.get("value")
    if payload.get("status") == "error":
        raise RuntimeError(f"Convex mutation {path} error: {payload.get('errorMessage')}")
    return payload


def call_query(
    path: str,
    args: dict[str, Any],
    *,
    url: Optional[str] = None,
    deploy_key: Optional[str] = None,
) -> Any:
    _load_env_files()

    convex_url = url or _convex_url()
    key = deploy_key or _convex_deploy_key()
    if not convex_url or not key:
        raise RuntimeError(
            "Convex URL and deploy key are not configured. "
            "Set CONVEX_URL and CONVEX_DEPLOY_KEY in your .env.local file."
        )

    response = requests.post(
        f"{convex_url.rstrip('/')}/api/query",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Convex {key}",
        },
        json={"path": path, "args": args, "format": "json"},
        verify=os.getenv("REQUESTS_CA_BUNDLE") or os.getenv("CURL_CA_BUNDLE") or True,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("status") == "error":
        raise RuntimeError(f"Convex query {path} error: {payload.get('errorMessage')}")
    return payload.get("value", payload)


def _push(function_path: str, args: dict[str, Any]) -> Any:
    if not _has_convex_config():
        print("Convex not configured; skipping push.")
        return None

    return call_mutation(function_path, args)


def push_resort_hours(
    resort_id: str,
    resort_name: str,
    source_url: str,
    sections: list[dict[str, Any]],
    *,
    function_path: str = "resortHours:save",
    fetched_at_ms: Optional[int] = None,
) -> Any:
    args = {
        "resortId": resort_id,
        "resortName": resort_name,
        "sourceUrl": source_url,
        "sections": sections,
    }
    if fetched_at_ms is not None:
        args["fetchedAt"] = fetched_at_ms

    return _push(function_path, args)


def push_resort_rates(
    resort_id: str,
    resort_name: str,
    source_url: str,
    rates: Any,
    *,
    function_path: str = "resortRates:save",
    fetched_at_ms: Optional[int] = None,
) -> Any:
    args = {
        "resortId": resort_id,
        "resortName": resort_name,
        "sourceUrl": source_url,
        "rates": rates,
    }
    if fetched_at_ms is not None:
        args["fetchedAt"] = fetched_at_ms

    return _push(function_path, args)


def push_resort_rentals(
    resort_id: str,
    resort_name: str,
    source_url: str,
    rentals: Any,
    *,
    function_path: str = "resortRentals:save",
    fetched_at_ms: Optional[int] = None,
) -> Any:
    args = {
        "resortId": resort_id,
        "resortName": resort_name,
        "sourceUrl": source_url,
        "rentals": rentals,
    }
    if fetched_at_ms is not None:
        args["fetchedAt"] = fetched_at_ms

    return _push(function_path, args)


def push_weather_and_status(
    resort_id: str,
    resort_name: str,
    source_url: str,
    weather_data: dict[str, Any],
    *,
    function_path: str = "weatherAndStatus:save",
    fetched_at_ms: Optional[int] = None,
) -> Any:
    args = {
        "resortId": resort_id,
        "resortName": resort_name,
        "sourceUrl": source_url,
        **weather_data,
    }
    if fetched_at_ms is not None:
        args["fetchedAt"] = fetched_at_ms

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
