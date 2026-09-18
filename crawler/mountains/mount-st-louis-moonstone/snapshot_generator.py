import json
import subprocess
import sys
from pathlib import Path

RESORT_ID = "mount-st-louis-moonstone"
RESORT_NAME = "Mount St. Louis Moonstone"
SKI_RESORT_FIELDS = {
    "tracks-green-length": "tracksGreenLength",
    "tracks-green-proportion": "tracksGreenProportion",
    "tracks-blue-length": "tracksBlueLength",
    "tracks-blue-proportion": "tracksBlueProportion",
    "tracks-black-length": "tracksBlackLength",
    "tracks-black-proportion": "tracksBlackProportion",
    "tracks-total-length": "tracksTotalLength",
}
TABLE_COLUMNS = {
    "resorts": [
        "resortId",
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
        "hasIceSkate",
        "hasAccommodations",
        "hasCrossCountry",
        "hasLessons",
        "hasSnowshoeing",
        "hasSpa",
        "hasTubing",
        "hasZipline",
        "phone",
        "rating",
        "ticketUrl",
        "tollFree",
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
    "weatherAndStatus": [
        "resortId",
        "sourceUrl",
        "updatedAt",
        "lifts",
        "tracks",
        "terrainParks",
    ],
}


def load_json(path):
    with path.open("r", encoding="utf-8") as source:
        return json.load(source)


def run_json_generators(directory):
    json_generators = directory / "json_generators"
    for script in sorted(json_generators.glob("*.py")):
        subprocess.run([sys.executable, str(script)], cwd=json_generators, check=True)


def build_snapshot(directory=None):
    directory = Path(directory) if directory is not None else Path(__file__).resolve().parent
    run_json_generators(directory)
    json_generators = directory / "json_generators"
    hours = load_json(json_generators / "hours-of-operation.json")
    ski_resort_info = load_json(json_generators / "skiresort.json")
    static_info = load_json(directory / "static_infos.json")
    weather = load_json(json_generators / "tracks-and-lifts-weather-status.json")
    resort = {
        **static_info,
        "resortId": RESORT_ID,
        "name": RESORT_NAME,
        "elevation": ski_resort_info["elevation"],
        "height": ski_resort_info["height"],
        **{
            target: ski_resort_info[source]
            for source, target in SKI_RESORT_FIELDS.items()
        },
    }

    return {
        "resortId": RESORT_ID,
        "tables": [
            {"table": "resorts", "content": resort},
            {"table": "resortHours", "content": hours},
            {"table": "weatherAndStatus", "content": weather},
        ],
    }


def has_value(content, column):
    value = content.get(column)
    return value not in (None, "", [], {})


def generate_report(snapshot, directory=None):
    directory = Path(directory) if directory is not None else Path(__file__).resolve().parent
    tables = []
    missing_column_count = 0
    for table in snapshot["tables"]:
        table_name = table["table"]
        missing_columns = [
            column
            for column in TABLE_COLUMNS[table_name]
            if not has_value(table.get("content", {}), column)
        ]
        missing_column_count += len(missing_columns)
        tables.append({"table": table_name, "missingColumns": missing_columns})

    report = {
        "resortId": snapshot["resortId"],
        "tables": tables,
        "missingColumnCount": missing_column_count,
    }
    with (directory / "snapshot_generator_report.json").open(
        "w", encoding="utf-8"
    ) as output:
        json.dump(report, output, indent=2, ensure_ascii=False)
    return report


def main():
    directory = Path(__file__).resolve().parent
    snapshot = build_snapshot(directory)
    with (directory / "snapshot_generator.json").open(
        "w", encoding="utf-8"
    ) as output:
        json.dump(snapshot, output, indent=2, ensure_ascii=False)
    generate_report(snapshot, directory)


if __name__ == "__main__":
    main()
