import json
import subprocess
import sys
from pathlib import Path

RESORT_DIR = Path(__file__).resolve().parent
CRAWLER_DIR = RESORT_DIR.parents[3]
SNAPSHOT_GENERATOR = RESORT_DIR / "snapshot_generator.py"
SNAPSHOT_FILE = RESORT_DIR / "snapshot_generator.json"
TABLE_NAMES = ("resorts", "resortHours", "resortRates", "resortRentals", "weatherAndStatus")
METADATA_FIELDS = {"resortId", "sourceUrl", "updatedAt"}
RESORT_INFO_FIELDS = ("hasIceSkate", "height")
sys.path.insert(0, str(CRAWLER_DIR))
from convex_client import push_resort_hours, push_resort_rates, push_resort_rentals, push_ski_resorts, push_weather_and_status

def main():
    subprocess.run([sys.executable, str(SNAPSHOT_GENERATOR)], cwd=RESORT_DIR, check=True)
    with SNAPSHOT_FILE.open(encoding="utf-8") as source: snapshot = json.load(source)
    contents = {item["table"]: item["content"] for item in snapshot["tables"]}
    if set(contents) != set(TABLE_NAMES): raise ValueError("Invalid snapshot tables")
    resort = contents["resorts"]
    if snapshot.get("resortId") != resort.get("resortId"): raise ValueError("Snapshot resort ID mismatch")
    for field in RESORT_INFO_FIELDS:
        if resort.get(field) in (None, ""): raise ValueError(f"Missing ski resort information: {field}")
    metadata = {name: (contents[name]["resortId"], contents[name]["sourceUrl"], contents[name]["updatedAt"]) for name in TABLE_NAMES[1:]}
    hours = contents["resortHours"]["hours"]
    if isinstance(hours, dict): hours = [{"name": "Hours of operation", "hours": [{"day": d, "time": t} for d, t in hours.items()]}]
    return {"resorts": push_ski_resorts([resort]), "resortHours": push_resort_hours(*metadata["resortHours"][:2], hours, updated_at_ms=metadata["resortHours"][2]), "resortRates": push_resort_rates(*metadata["resortRates"][:2], contents["resortRates"]["rates"], updated_at_ms=metadata["resortRates"][2]), "resortRentals": push_resort_rentals(*metadata["resortRentals"][:2], contents["resortRentals"]["rentals"], updated_at_ms=metadata["resortRentals"][2]), "weatherAndStatus": push_weather_and_status(*metadata["weatherAndStatus"][:2], {k: v for k, v in contents["weatherAndStatus"].items() if k not in METADATA_FIELDS}, updated_at_ms=metadata["weatherAndStatus"][2])}

if __name__ == "__main__": main()
