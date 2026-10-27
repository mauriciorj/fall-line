import json
import subprocess
import sys
import time
from pathlib import Path


RESORT_ID = "banff-sunshine"
RESORT_NAME = "Banff Sunshine"
PUBLISHED = True
SKI_RESORT_SOURCE_URL = "https://www.skiresort.com/en/ski-resort/banff-sunshine/"
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
DIFFICULTY_FIELDS = {
    "easy": "green",
    "medium": "blue",
    "hard": "black",
    "black": "black",
    "blue": "blue",
    "doubleblack": "doubleBlack",
    "double black": "doubleBlack",
    "freestyle": "freeStyle",
    "free style": "freeStyle",
    "green": "green",
}
TABLE_COLUMNS = {
    "resorts": [
        "resortId",
        "sourceUrl",
        "updatedAt",
        "published",
        "name",
        "continent",
        "country",
        "region",
        "website",
        "address",
        "coordinates",
        "email",
        "googleMapsUrl",
        "phone",
        "tracksSummary",
        "elevation",
        "height",
        "tracksGreenLength",
        "tracksGreenProportion",
        "tracksBlueLength",
        "tracksBlueProportion",
        "tracksBlackLength",
        "tracksBlackProportion",
        "tracksTotalLength",
    ],
    "resortHours": ["resortId", "sourceUrl", "updatedAt", "hours"],
    "resortRates": ["resortId", "sourceUrl", "updatedAt", "rates"],
    "resortRentals": ["resortId", "sourceUrl", "updatedAt", "rentals"],
    "weatherAndStatus": ["resortId", "sourceUrl", "updatedAt", "lifts", "tracks"],
}
EMPTY_TRACKS_SUMMARY = {
    "black": 0,
    "blue": 0,
    "doubleBlack": 0,
    "freeStyle": 0,
    "green": 0,
}


def load_json(path):
    with path.open("r", encoding="utf-8") as source:
        return json.load(source)


def run_json_generators(directory):
    generator_dir = directory / "json_generators"
    script = generator_dir / "skiresort.py"
    subprocess.run([sys.executable, str(script)], cwd=generator_dir, check=True)


def build_tracks_summary(weather=None):
    summary = dict(EMPTY_TRACKS_SUMMARY)
    for track in (weather or {}).get("tracks", []):
        field = DIFFICULTY_FIELDS.get(str(track.get("difficulty", "")).strip().lower())
        if field:
            summary[field] += 1
    return summary


def build_resort(static_info, ski_resort_info, updated_at):
    resort = dict(static_info)
    resort.update(
        {
            "resortId": RESORT_ID,
            "sourceUrl": SKI_RESORT_SOURCE_URL,
            "updatedAt": updated_at,
            "name": RESORT_NAME,
            "published": PUBLISHED,
            "tracksSummary": build_tracks_summary(),
        }
    )
    for source_field, resort_field in SKI_RESORT_FIELDS.items():
        value = ski_resort_info.get(source_field)
        if value not in (None, ""):
            resort[resort_field] = value
    return resort


def build_empty_table(table_name, updated_at):
    content = {
        "resortId": RESORT_ID,
        "sourceUrl": SKI_RESORT_SOURCE_URL,
        "updatedAt": updated_at,
    }
    if table_name == "resortHours":
        content["hours"] = []
    elif table_name == "resortRates":
        content["rates"] = {}
    elif table_name == "resortRentals":
        content["rentals"] = {}
    elif table_name == "weatherAndStatus":
        content.update({"lifts": [], "tracks": []})
    else:
        raise ValueError(f"Unsupported empty table: {table_name}")
    return content


def build_snapshot(directory=None):
    directory = Path(directory) if directory is not None else Path(__file__).resolve().parent
    generator_dir = directory / "json_generators"
    run_json_generators(directory)

    static_info = load_json(directory / "static_infos.json")
    if static_info.get("resortId") != RESORT_ID:
        raise ValueError("static_infos.json resortId does not match the crawler")

    updated_at = int(time.time() * 1000)
    tables = [
        {
            "table": "resorts",
            "content": build_resort(
                static_info,
                load_json(generator_dir / "skiresort.json"),
                updated_at,
            ),
        }
    ]
    for table_name in ("resortHours", "resortRates", "resortRentals", "weatherAndStatus"):
        tables.append(
            {
                "table": table_name,
                "content": build_empty_table(table_name, updated_at),
            }
        )
    return {"resortId": RESORT_ID, "tables": tables}


def has_value(content, column):
    return content.get(column) not in (None, "", [], {})


def generate_report(snapshot, directory=None):
    directory = Path(directory) if directory is not None else Path(__file__).resolve().parent
    tables = []
    missing_count = 0
    for table in snapshot["tables"]:
        table_name = table["table"]
        missing_columns = [
            column
            for column in TABLE_COLUMNS[table_name]
            if not has_value(table.get("content", {}), column)
        ]
        missing_count += len(missing_columns)
        tables.append({"table": table_name, "missingColumns": missing_columns})
    report = {
        "resortId": snapshot["resortId"],
        "tables": tables,
        "missingColumnCount": missing_count,
    }
    with (directory / "snapshot_generator_report.json").open("w", encoding="utf-8") as output:
        json.dump(report, output, indent=2, ensure_ascii=False)
    return report


def main():
    directory = Path(__file__).resolve().parent
    snapshot = build_snapshot(directory)
    with (directory / "snapshot_generator.json").open("w", encoding="utf-8") as output:
        json.dump(snapshot, output, indent=2, ensure_ascii=False)
    generate_report(snapshot, directory)


if __name__ == "__main__":
    main()