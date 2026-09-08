import json
import subprocess
import sys
from pathlib import Path

LAKERIDGE_DIR = Path(__file__).resolve().parent
CRAWLER_DIR = LAKERIDGE_DIR.parents[1]
SNAPSHOT_GENERATOR = LAKERIDGE_DIR / "snapshot_generator.py"
SNAPSHOT_FILE = LAKERIDGE_DIR / "snapshot_generator.json"
TABLE_NAMES = (
    "resorts", "resortHours", "resortRates", "resortRentals", "weatherAndStatus",
)
METADATA_FIELDS = {"resortId", "sourceUrl", "updatedAt"}

sys.path.insert(0, str(CRAWLER_DIR))
from convex_client import (
    push_resort_hours,
    push_resort_rates,
    push_resort_rentals,
    push_ski_resorts,
    push_weather_and_status,
)


def run_snapshot_generator():
    subprocess.run([sys.executable, str(SNAPSHOT_GENERATOR)], cwd=LAKERIDGE_DIR, check=True)


def load_snapshot():
    with SNAPSHOT_FILE.open("r", encoding="utf-8") as source:
        return json.load(source)


def get_table_contents(snapshot):
    tables = snapshot.get("tables")
    if not isinstance(tables, list):
        raise ValueError("Snapshot tables must be a list")
    contents = {}
    for table in tables:
        table_name = table.get("table")
        if table_name in contents:
            raise ValueError(f"Duplicate table in snapshot: {table_name}")
        content = table.get("content")
        if not isinstance(content, dict):
            raise ValueError(f"Table content must be an object: {table_name}")
        contents[table_name] = content
    missing = set(TABLE_NAMES) - contents.keys()
    unexpected = contents.keys() - set(TABLE_NAMES)
    if missing or unexpected:
        raise ValueError(f"Invalid snapshot tables; missing={sorted(missing)}, unexpected={sorted(unexpected)}")
    return contents


def require_metadata(content, table_name):
    missing = METADATA_FIELDS - content.keys()
    if missing:
        raise ValueError(f"Missing metadata in {table_name}: {sorted(missing)}")
    return content["resortId"], content["sourceUrl"], content["updatedAt"]


def push_snapshot(snapshot):
    contents = get_table_contents(snapshot)
    resort_id = contents["resorts"].get("resortId")
    if not isinstance(resort_id, str) or not resort_id:
        raise ValueError("Missing resortId in resorts")
    if snapshot.get("resortId") != resort_id:
        raise ValueError(f"Snapshot resort ID mismatch: {snapshot.get('resortId')} != {resort_id}")
    metadata = {
        name: require_metadata(contents[name], name)
        for name in TABLE_NAMES[1:]
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
    return {
        "resorts": push_ski_resorts([contents["resorts"]]),
        "resortHours": push_resort_hours(hours_id, hours_url, hours["hours"], updated_at_ms=hours_time),
        "resortRates": push_resort_rates(rates_id, rates_url, rates["rates"], updated_at_ms=rates_time),
        "resortRentals": push_resort_rentals(rentals_id, rentals_url, rentals["rentals"], updated_at_ms=rentals_time),
        "weatherAndStatus": push_weather_and_status(
            weather_id, weather_url,
            {key: value for key, value in weather.items() if key not in METADATA_FIELDS},
            updated_at_ms=weather_time,
        ),
    }


def main():
    run_snapshot_generator()
    return push_snapshot(load_snapshot())


if __name__ == "__main__":
    main()
