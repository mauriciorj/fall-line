import json
import re
import subprocess
import sys
from pathlib import Path

RESORT_ID = "devils-glen"
RESORT_NAME = "Devil's Glen Country Club"
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
        "resortId", "published", "name", "continent", "country", "region",
        "website", "address", "email", "hasIceSkate", "hasAccommodations",
        "hasCrossCountry", "hasLessons", "hasSnowshoeing", "hasSpa", "hasTubing",
        "hasZipline", "dayTicketPrice", "phone", "tracksSummary", "elevation",
        "height", "tracksGreenLength", "tracksGreenProportion", "tracksBlueLength",
        "tracksBlueProportion", "tracksBlackLength", "tracksBlackProportion",
        "tracksTotalLength", "ticketUrl",
    ],
    "resortHours": ["resortId", "sourceUrl", "updatedAt", "hours"],
    "resortRates": ["resortId", "sourceUrl", "updatedAt", "rates"],
    "resortRentals": ["resortId", "sourceUrl", "updatedAt", "rentals"],
    "weatherAndStatus": [
        "resortId", "sourceUrl", "updatedAt", "lifts", "tracks", "terrainParks",
    ],
}
DIFFICULTY_FIELDS = {
    "black": "black",
    "blue": "blue",
    "doubleblack": "doubleBlack",
    "freestyle": "freeStyle",
    "green": "green",
}


def load_json(path):
    with path.open("r", encoding="utf-8") as source:
        return json.load(source)


def parse_price(value):
    if value in (None, ""):
        return None
    match = re.search(r"\d[\d,.]*", str(value))
    if not match:
        return None
    amount = float(match.group().replace(",", ""))
    return int(amount) if amount.is_integer() else amount


def build_tracks_summary(weather):
    summary = {field: 0 for field in ["black", "blue", "doubleBlack", "freeStyle", "green"]}
    tracks = weather.get("tracks", []) + weather.get("terrainParks", [])
    for track in tracks:
        field = DIFFICULTY_FIELDS.get(str(track.get("difficulty", "")).lower())
        if field:
            summary[field] += 1
    return summary


def get_rate_price(rates):
    return parse_price(rates.get("rates", {}).get("day-week", {}).get("adults"))


def build_resort(static_info, rates, weather, ski_resort_info):
    resort = {**static_info, "resortId": RESORT_ID, "name": RESORT_NAME}
    for source_field, resort_field in SKI_RESORT_FIELDS.items():
        value = ski_resort_info.get(source_field)
        if value not in (None, ""):
            resort[resort_field] = value
    resort["elevation"] = ski_resort_info.get("elevation")
    resort["height"] = ski_resort_info.get("height")
    resort["tracksSummary"] = build_tracks_summary(weather)
    day_ticket_price = get_rate_price(rates)
    if day_ticket_price is not None:
        resort["dayTicketPrice"] = day_ticket_price
    return resort


def run_json_generators(directory):
    json_generators = directory / "json_generators"
    for script in sorted(json_generators.glob("*.py")):
        subprocess.run([sys.executable, str(script)], cwd=json_generators, check=True)


def build_snapshot(directory=None):
    directory = Path(directory) if directory is not None else Path(__file__).resolve().parent
    run_json_generators(directory)
    json_generators = directory / "json_generators"
    hours = load_json(json_generators / "hours-of-operation.json")
    rates = load_json(json_generators / "lift-rates.json")
    rentals = load_json(json_generators / "rentals.json")
    weather = load_json(json_generators / "tracks-and-lifts-weather-status.json")
    ski_resort_info = load_json(json_generators / "skiresort.json")
    static_info = load_json(directory / "static_infos.json")
    return {
        "resortId": RESORT_ID,
        "tables": [
            {"table": "resorts", "content": build_resort(static_info, rates, weather, ski_resort_info)},
            {"table": "resortHours", "content": hours},
            {"table": "resortRates", "content": rates},
            {"table": "resortRentals", "content": rentals},
            {"table": "weatherAndStatus", "content": weather},
        ],
    }


def generate_report(snapshot, directory=None):
    directory = Path(directory) if directory is not None else Path(__file__).resolve().parent
    tables = []
    missing_column_count = 0
    for table in snapshot["tables"]:
        table_name = table["table"]
        missing_columns = [
            column for column in TABLE_COLUMNS[table_name]
            if table.get("content", {}).get(column) in (None, "", [], {})
        ]
        missing_column_count += len(missing_columns)
        tables.append({"table": table_name, "missingColumns": missing_columns})
    report = {"resortId": snapshot["resortId"], "tables": tables, "missingColumnCount": missing_column_count}
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
