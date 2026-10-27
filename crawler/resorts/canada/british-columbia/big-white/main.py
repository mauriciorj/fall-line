import json
import subprocess
import sys
from pathlib import Path

BIG_WHITE_DIR = Path(__file__).resolve().parent
CRAWLER_DIR = BIG_WHITE_DIR.parents[3]
SNAPSHOT_GENERATOR = BIG_WHITE_DIR / "snapshot_generator.py"
SNAPSHOT_FILE = BIG_WHITE_DIR / "snapshot_generator.json"
TABLE_NAMES = ("resorts", "resortHours", "resortRates", "resortRentals", "weatherAndStatus")
METADATA_FIELDS = {"resortId", "sourceUrl", "updatedAt"}
RESORT_INFO_FIELDS = ("elevation", "height", "tracksGreenLength", "tracksGreenProportion", "tracksBlueLength", "tracksBlueProportion", "tracksBlackLength", "tracksBlackProportion", "tracksTotalLength")

sys.path.insert(0, str(CRAWLER_DIR))
from convex_client import push_resort_hours, push_resort_rates, push_resort_rentals, push_ski_resorts, push_weather_and_status


def run_snapshot_generator():
    subprocess.run([sys.executable, str(SNAPSHOT_GENERATOR)], cwd=BIG_WHITE_DIR, check=True)


def load_snapshot():
    with SNAPSHOT_FILE.open("r", encoding="utf-8") as source:
        return json.load(source)


def get_table_contents(snapshot):
    tables = snapshot.get("tables")
    if not isinstance(tables, list):
        raise ValueError("Snapshot tables must be a list")
    contents = {}
    for table in tables:
        name = table.get("table")
        content = table.get("content")
        if name in contents or not isinstance(content, dict):
            raise ValueError(f"Invalid table: {name}")
        contents[name] = content
    missing = set(TABLE_NAMES) - contents.keys()
    unexpected = contents.keys() - set(TABLE_NAMES)
    if missing or unexpected:
        raise ValueError(f"Invalid snapshot tables; missing={sorted(missing)}, unexpected={sorted(unexpected)}")
    return contents


def require_metadata(content, name):
    missing = METADATA_FIELDS - content.keys()
    if missing:
        raise ValueError(f"Missing metadata in {name}: {sorted(missing)}")
    return content["resortId"], content["sourceUrl"], content["updatedAt"]


def push_snapshot(snapshot):
    content = get_table_contents(snapshot)
    resort_id = content["resorts"].get("resortId")
    if snapshot.get("resortId") != resort_id:
        raise ValueError("Snapshot resort ID mismatch")
    missing = [field for field in RESORT_INFO_FIELDS if content["resorts"].get(field) in (None, "")]
    if missing:
        raise ValueError(f"Missing ski resort information: {sorted(missing)}")
    metadata = {name: require_metadata(content[name], name) for name in TABLE_NAMES[1:]}
    for name, (table_id, _, _) in metadata.items():
        if table_id != resort_id:
            raise ValueError(f"Resort ID mismatch in {name}")
    hours, rates, rentals, weather = (content[name] for name in TABLE_NAMES[1:])
    hours_id, hours_url, hours_time = metadata["resortHours"]
    rates_id, rates_url, rates_time = metadata["resortRates"]
    rentals_id, rentals_url, rentals_time = metadata["resortRentals"]
    weather_id, weather_url, weather_time = metadata["weatherAndStatus"]
    hours_data = hours["hours"]
    if isinstance(hours_data, dict):
        hours_data = [{"name": "Hours of operation", "hours": [{"day": day, "time": time} for day, time in hours_data.items()]}]
    weather_data = {key: value for key, value in weather.items() if key not in METADATA_FIELDS}
    weather_data["trails"] = weather_data.pop("tracks", [])
    return {
        "resorts": push_ski_resorts([content["resorts"]]),
        "resortHours": push_resort_hours(hours_id, hours_url, hours_data, updated_at_ms=hours_time),
        "resortRates": push_resort_rates(rates_id, rates_url, rates["rates"], updated_at_ms=rates_time),
        "resortRentals": push_resort_rentals(rentals_id, rentals_url, rentals["rentals"], updated_at_ms=rentals_time),
        "weatherAndStatus": push_weather_and_status(weather_id, weather_url, weather_data, updated_at_ms=weather_time),
    }


def main():
    run_snapshot_generator()
    return push_snapshot(load_snapshot())


if __name__ == "__main__":
    main()
