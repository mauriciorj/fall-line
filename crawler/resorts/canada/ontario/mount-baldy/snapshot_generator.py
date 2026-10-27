import json
import re
import subprocess
import sys
from pathlib import Path

RESORT_ID = "mount-baldy"
RESORT_NAME = "Mount Baldy"
TABLE_COLUMNS = {
    "resorts": [
        "resortId", "published", "name", "continent", "country", "region", "website", "address",
        "coordinates", "dayTicketPrice", "email", "googleMapsUrl", "hasIceSkate", "hasAccommodations",
        "hasCrossCountry", "hasLessons", "hasSnowshoeing", "hasSpa", "hasTubing", "hasZipline",
        "lessonsPrice", "phone", "rating", "skiRentalPrice", "snowBoardRentalPrice", "tracksSummary",
        "elevation", "height", "tracksGreenLength", "tracksGreenProportion", "tracksBlueLength",
        "tracksBlueProportion", "tracksBlackLength", "tracksBlackProportion", "tracksTotalLength",
        "ticketUrl", "tollFree", "tubbingPrice",
    ],
    "resortHours": ["resortId", "sourceUrl", "updatedAt", "hours"],
    "resortRates": ["resortId", "sourceUrl", "updatedAt", "rates"],
    "resortRentals": ["resortId", "sourceUrl", "updatedAt", "rentals"],
    "weatherAndStatus": ["resortId", "sourceUrl", "updatedAt", "lifts", "tracks", "terrainParks"],
}
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
    "black": "black",
    "blue": "blue",
    "doubleblack": "doubleBlack",
    "double black": "doubleBlack",
    "freestyle": "freeStyle",
    "free style": "freeStyle",
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
    for track in weather.get("tracks", []) + weather.get("terrainParks", []):
        field = DIFFICULTY_FIELDS.get(str(track.get("difficulty", "")).lower())
        if field:
            summary[field] += 1
    return summary


def get_rate_price(rates):
    return parse_price(rates.get("rates", {}).get("day-week", {}).get("adults"))


def get_rental_price(rentals):
    return parse_price(rentals.get("rentals", {}).get("ski", {}).get("adults"))


def build_resort(static_info, rates, rentals, weather, ski_resort_info=None):
    resort = dict(static_info)
    resort["resortId"] = RESORT_ID
    resort["name"] = RESORT_NAME
    for source_field, resort_field in SKI_RESORT_FIELDS.items():
        value = (ski_resort_info or {}).get(source_field)
        if value not in (None, ""):
            resort[resort_field] = value
    resort["hasAccommodations"] = bool(static_info.get("resort_accommodations"))
    resort["tracksSummary"] = build_tracks_summary(weather)
    day_price = get_rate_price(rates)
    rental_price = get_rental_price(rentals)
    if day_price is not None:
        resort["dayTicketPrice"] = day_price
    if rental_price is not None:
        resort["skiRentalPrice"] = rental_price
        resort["snowBoardRentalPrice"] = rental_price
    return resort


def run_json_generators(directory):
    json_generators = directory / "json_generators"
    for script in sorted(json_generators.glob("*.py")):
        subprocess.run([sys.executable, str(script)], cwd=json_generators, check=True)


def build_snapshot(directory=None):
    directory = Path(directory) if directory is not None else Path(__file__).resolve().parent
    run_json_generators(directory)
    generators = directory / "json_generators"
    hours = load_json(generators / "hours-of-operation.json")
    rates = load_json(generators / "lift-rates.json")
    rentals = load_json(generators / "rentals.json")
    weather = load_json(generators / "tracks-and-lifts-weather-status.json")
    ski_resort_info = load_json(generators / "skiresort.json")
    static_info = load_json(directory / "static_infos.json")
    return {"resortId": RESORT_ID, "tables": [
        {"table": "resorts", "content": build_resort(static_info, rates, rentals, weather, ski_resort_info)},
        {"table": "resortHours", "content": hours},
        {"table": "resortRates", "content": rates},
        {"table": "resortRentals", "content": rentals},
        {"table": "weatherAndStatus", "content": weather},
    ]}


def has_value(content, column):
    return content.get(column) not in (None, "", [], {})


def generate_report(snapshot, directory=None):
    directory = Path(directory) if directory is not None else Path(__file__).resolve().parent
    tables = []
    missing_count = 0
    for table in snapshot["tables"]:
        name = table["table"]
        missing = [column for column in TABLE_COLUMNS[name] if not has_value(table.get("content", {}), column)]
        missing_count += len(missing)
        tables.append({"table": name, "missingColumns": missing})
    report = {"resortId": snapshot["resortId"], "tables": tables, "missingColumnCount": missing_count}
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
