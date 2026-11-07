import json
import subprocess
import sys
from pathlib import Path

RESORT_DIR = Path(__file__).resolve().parent
CRAWLER_DIR = RESORT_DIR.parents[3]
JSON_GENERATORS_DIR = RESORT_DIR / "json_generators"
SKIRESORT_GENERATOR = JSON_GENERATORS_DIR / "skiresort.py"
SKIRESORT_FILE = JSON_GENERATORS_DIR / "skiresort.json"
STATIC_INFOS_FILE = RESORT_DIR / "static_infos.json"
BASICS_FILE = RESORT_DIR / "basics.json"

RESORT_ID = "chicopee"
RESORT_NAME = "Chicopee"
TABLE_NAME = "resorts"
SKI_RESORT_FIELDS = {
    "elevation": "elevation",
    "height": "height",
    "tracks-green-length": "tracksGreenLength",
    "tracks-green-proportion": "tracksGreenProportion",
    "tracks-blue-length": "tracksBlueLength",
    "tracks-blue-proportion": "tracksBlueProportion",
    "tracks-black-length": "tracksBlackLength",
    "tracks-black-proportion": "tracksBlackProportion",
    "tracks-total-length": "tracksTotalLength",
}
REQUIRED_FIELDS = ("resortId", "name", *SKI_RESORT_FIELDS.values())


def load_json(path):
    with path.open("r", encoding="utf-8") as source:
        return json.load(source)


def run_skiresort_generator():
    subprocess.run(
        [sys.executable, str(SKIRESORT_GENERATOR)],
        cwd=JSON_GENERATORS_DIR,
        check=True,
    )


def normalize_coordinates(coordinates):
    return {key: float(value) for key, value in coordinates.items()}


def build_resort(static_info, ski_resort_info):
    resort = {}
    for source_field, resort_field in SKI_RESORT_FIELDS.items():
        value = ski_resort_info.get(source_field)
        if value not in (None, ""):
            resort[resort_field] = value

    resort.update(
        {key: value for key, value in static_info.items() if value not in (None, "")}
    )
    resort["name"] = static_info.get("name") or RESORT_NAME
    resort["resortId"] = RESORT_ID
    coordinates = resort.get("coordinates")
    if isinstance(coordinates, dict) and all(
        coordinates.get(key) not in (None, "") for key in ("lat", "lng")
    ):
        resort["coordinates"] = normalize_coordinates(coordinates)
    else:
        resort.pop("coordinates", None)
    return resort


def build_basics():
    return {
        "resortId": RESORT_ID,
        "tables": [
            {
                "table": TABLE_NAME,
                "content": build_resort(
                    load_json(STATIC_INFOS_FILE), load_json(SKIRESORT_FILE)
                ),
            }
        ],
    }


def write_basics(basics):
    with BASICS_FILE.open("w", encoding="utf-8") as output:
        json.dump(basics, output, indent=2, ensure_ascii=False)


def validate_basics(basics):
    tables = basics.get("tables")
    if not isinstance(tables, list) or len(tables) != 1:
        raise ValueError("Basics must contain exactly one table")
    table = tables[0]
    if table.get("table") != TABLE_NAME:
        raise ValueError(f"Unexpected table: {table.get('table')}")

    content = table.get("content")
    if not isinstance(content, dict):
        raise ValueError("Resort content must be an object")
    if content.get("resortId") != RESORT_ID or basics.get("resortId") != RESORT_ID:
        raise ValueError("Resort ID mismatch in basics")

    missing = [field for field in REQUIRED_FIELDS if content.get(field) in (None, "")]
    if missing:
        raise ValueError(f"Missing ski resort information: {sorted(missing)}")
    return content


def push_basics(basics):
    sys.path.insert(0, str(CRAWLER_DIR))
    from convex_client import push_ski_resorts

    return push_ski_resorts([validate_basics(basics)])


def main():
    run_skiresort_generator()
    basics = build_basics()
    write_basics(basics)
    return push_basics(basics)


if __name__ == "__main__":
    main()
