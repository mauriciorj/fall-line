import json
import subprocess
import sys
from pathlib import Path


BANFF_SUNSHINE_DIR = Path(__file__).resolve().parent
CRAWLER_DIR = BANFF_SUNSHINE_DIR.parents[3]
SNAPSHOT_GENERATOR = BANFF_SUNSHINE_DIR / "snapshot_generator.py"
SNAPSHOT_FILE = BANFF_SUNSHINE_DIR / "snapshot_generator.json"
TABLE_NAMES = ("resorts", "resortHours", "resortRates", "resortRentals", "weatherAndStatus")
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
    subprocess.run([sys.executable, str(SNAPSHOT_GENERATOR)], cwd=BANFF_SUNSHINE_DIR, check=True)


def load_snapshot():
    with SNAPSHOT_FILE.open("r", encoding="utf-8") as source:
        return json.load(source)


def get_table_contents(snapshot):
    tables = snapshot.get("tables")
    if not isinstance(tables, list):
        raise ValueError("Snapshot tables must be a list")

    contents = {}
    for table in tables:
        if not isinstance(table, dict):
            raise ValueError("Each snapshot table must be an object")
        name = table.get("table")
        if not isinstance(name, str):
            raise ValueError("Each snapshot table must have a string name")
        content = table.get("content")
        if name in contents:
            raise ValueError(f"Duplicate table in snapshot: {name}")
        if not isinstance(content, dict):
            raise ValueError(f"Table content must be an object: {name}")
        contents[name] = content

    missing = set(TABLE_NAMES) - contents.keys()
    unexpected = contents.keys() - set(TABLE_NAMES)
    if missing or unexpected:
        raise ValueError(
            f"Invalid snapshot tables; missing={sorted(missing)}, unexpected={sorted(unexpected)}"
        )
    return contents


def require_metadata(content, table_name):
    missing = METADATA_FIELDS - content.keys()
    if missing:
        raise ValueError(f"Missing metadata in {table_name}: {sorted(missing)}")

    resort_id = content["resortId"]
    source_url = content["sourceUrl"]
    updated_at = content["updatedAt"]
    if not isinstance(resort_id, str) or not resort_id:
        raise ValueError(f"Invalid resortId in {table_name}")
    if not isinstance(source_url, str) or not source_url:
        raise ValueError(f"Invalid sourceUrl in {table_name}")
    if isinstance(updated_at, bool) or not isinstance(updated_at, (int, float)):
        raise ValueError(f"Invalid updatedAt in {table_name}")
    return resort_id, source_url, updated_at


def normalize_weather_data(weather):
    normalized = {
        key: value for key, value in weather.items() if key not in METADATA_FIELDS
    }
    normalized["trails"] = normalized.pop("tracks", [])
    normalized["lifts"] = [
        {key: value for key, value in lift.items() if key != "area"}
        for lift in normalized.get("lifts", [])
    ]
    return normalized


def push_snapshot(snapshot):
    contents = get_table_contents(snapshot)
    resort = contents["resorts"]
    resort_id = resort.get("resortId")
    if not isinstance(resort_id, str) or not resort_id:
        raise ValueError("Missing resortId in resorts")
    if snapshot.get("resortId") != resort_id:
        raise ValueError("Snapshot resort ID mismatch")
    if resort.get("published") is not True:
        raise ValueError("Banff Sunshine must be published before publishing")

    require_metadata(resort, "resorts")
    missing_resort_info = [
        field for field in RESORT_INFO_FIELDS if resort.get(field) in (None, "")
    ]
    if missing_resort_info:
        raise ValueError(f"Missing ski resort information: {sorted(missing_resort_info)}")

    metadata = {
        name: require_metadata(contents[name], name) for name in TABLE_NAMES[1:]
    }
    for name, (table_resort_id, _, _) in metadata.items():
        if table_resort_id != resort_id:
            raise ValueError(f"Resort ID mismatch in {name}: {table_resort_id} != {resort_id}")

    hours = contents["resortHours"]
    rates = contents["resortRates"]
    rentals = contents["resortRentals"]
    weather = contents["weatherAndStatus"]
    hours_id, hours_url, hours_time = metadata["resortHours"]
    rates_id, rates_url, rates_time = metadata["resortRates"]
    rentals_id, rentals_url, rentals_time = metadata["resortRentals"]
    weather_id, weather_url, weather_time = metadata["weatherAndStatus"]

    hours_data = hours.get("hours")
    if not isinstance(hours_data, (dict, list)):
        raise ValueError("resortHours.hours must be an object or list")
    if isinstance(hours_data, dict):
        hours_data = [
            {
                "name": "Hours of operation",
                "hours": [
                    {"day": day, "time": time} for day, time in hours_data.items()
                ],
            }
        ]

    rates_data = rates.get("rates")
    rentals_data = rentals.get("rentals")
    if rates_data is None:
        raise ValueError("Missing resortRates.rates")
    if rentals_data is None:
        raise ValueError("Missing resortRentals.rentals")
    if not isinstance(weather.get("lifts"), list) or not isinstance(
        weather.get("tracks"), list
    ):
        raise ValueError("weatherAndStatus.lifts and tracks must be lists")

    return {
        "resorts": push_ski_resorts([resort]),
        "resortHours": push_resort_hours(
            hours_id, hours_url, hours_data, updated_at_ms=hours_time
        ),
        "resortRates": push_resort_rates(
            rates_id, rates_url, rates_data, updated_at_ms=rates_time
        ),
        "resortRentals": push_resort_rentals(
            rentals_id, rentals_url, rentals_data, updated_at_ms=rentals_time
        ),
        "weatherAndStatus": push_weather_and_status(
            weather_id,
            weather_url,
            normalize_weather_data(weather),
            updated_at_ms=weather_time,
        ),
    }


def main():
    run_snapshot_generator()
    return push_snapshot(load_snapshot())


if __name__ == "__main__":
    main()