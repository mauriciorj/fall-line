import json, subprocess, sys
from pathlib import Path

SILVERSTAR_DIR = Path(__file__).resolve().parent
CRAWLER_DIR = SILVERSTAR_DIR.parents[3]
SNAPSHOT_GENERATOR = SILVERSTAR_DIR / "snapshot_generator.py"
SNAPSHOT_FILE = SILVERSTAR_DIR / "snapshot_generator.json"
TABLE_NAMES = (
    "resorts",
    "resortHours",
    "resortRates",
    "resortRentals",
    "weatherAndStatus",
)
METADATA_FIELDS = {"resortId", "sourceUrl", "updatedAt"}
RESORT_INFO_FIELDS = (
    "elevation",
    "height",
    "tracksGreenLength",
    "tracksGreenProportion",
    "tracksBlueLength",
    "tracksBlueProportion",
    "tracksBlackLength",
    "tracksBlackProportion",
    "tracksTotalLength",
)
sys.path.insert(0, str(CRAWLER_DIR))
from convex_client import (
    push_resort_hours,
    push_resort_rates,
    push_resort_rentals,
    push_ski_resorts,
    push_weather_and_status,
)


def run_snapshot_generator():
    subprocess.run(
        [sys.executable, str(SNAPSHOT_GENERATOR)], cwd=SILVERSTAR_DIR, check=True
    )


def load_snapshot():
    with SNAPSHOT_FILE.open("r", encoding="utf-8") as source:
        return json.load(source)


def tables(snapshot):
    result = {}
    for table in snapshot.get("tables", []):
        name = table.get("table")
        content = table.get("content")
        if name in result or not isinstance(content, dict):
            raise ValueError(f"Invalid table: {name}")
        result[name] = content
    if set(result) != set(TABLE_NAMES):
        raise ValueError("Invalid snapshot tables")
    return result


def metadata(content, name):
    missing = METADATA_FIELDS - content.keys()
    if missing:
        raise ValueError(f"Missing metadata in {name}: {sorted(missing)}")
    return content["resortId"], content["sourceUrl"], content["updatedAt"]


def push_snapshot(snapshot):
    content = tables(snapshot)
    resort_id = content["resorts"].get("resortId")
    if snapshot.get("resortId") != resort_id:
        raise ValueError("Snapshot resort ID mismatch")
    missing = [
        field
        for field in RESORT_INFO_FIELDS
        if content["resorts"].get(field) in (None, "")
    ]
    if missing:
        raise ValueError(f"Missing ski resort information: {sorted(missing)}")
    meta = {name: metadata(content[name], name) for name in TABLE_NAMES[1:]}
    for name, (table_id, _, _) in meta.items():
        if table_id != resort_id:
            raise ValueError(f"Resort ID mismatch in {name}")
    hours, rates, rentals, weather = (content[name] for name in TABLE_NAMES[1:])
    h_id, h_url, h_time = meta["resortHours"]
    r_id, r_url, r_time = meta["resortRates"]
    n_id, n_url, n_time = meta["resortRentals"]
    w_id, w_url, w_time = meta["weatherAndStatus"]
    hours_data = hours["hours"]
    if isinstance(hours_data, dict):
        hours_data = [
            {
                "name": "Hours of operation",
                "hours": [{"day": d, "time": t} for d, t in hours_data.items()],
            }
        ]
    weather_data = {k: v for k, v in weather.items() if k not in METADATA_FIELDS}
    weather_data["trails"] = weather_data.pop("tracks", [])
    return {
        "resorts": push_ski_resorts([content["resorts"]]),
        "resortHours": push_resort_hours(h_id, h_url, hours_data, updated_at_ms=h_time),
        "resortRates": push_resort_rates(
            r_id, r_url, rates["rates"], updated_at_ms=r_time
        ),
        "resortRentals": push_resort_rentals(
            n_id, n_url, rentals["rentals"], updated_at_ms=n_time
        ),
        "weatherAndStatus": push_weather_and_status(
            w_id, w_url, weather_data, updated_at_ms=w_time
        ),
    }


def main():
    run_snapshot_generator()
    return push_snapshot(load_snapshot())


if __name__ == "__main__":
    main()
