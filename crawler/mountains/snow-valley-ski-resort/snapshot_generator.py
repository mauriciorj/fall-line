import json
import re
import subprocess
import sys
from pathlib import Path

RESORT_ID = "snow-valley-ski-resort"
RESORT_NAME = "Snow Valley Ski Resort"
TABLE_COLUMNS = {
    "resorts": ["resortId", "published", "name", "continent", "country", "region", "website", "address", "coordinates", "dayTicketPrice", "email", "googleMapsUrl", "hasAccommodations", "hasCrossCountry", "hasLessons", "hasSnowshoeing", "hasSpa", "hasTubing", "hasZipline", "lessonsPrice", "phone", "rating", "skiRentalPrice", "snowBoardRentalPrice", "tracksSummary", "ticketUrl", "tollFree", "tubbingPrice"],
    "resortHours": ["resortId", "sourceUrl", "updatedAt", "hours"],
    "resortRates": ["resortId", "sourceUrl", "updatedAt", "rates"],
    "resortRentals": ["resortId", "sourceUrl", "updatedAt", "rentals"],
    "weatherAndStatus": ["resortId", "sourceUrl", "updatedAt", "lifts", "tracks"],
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
    for track in weather.get("tracks", []):
        field = DIFFICULTY_FIELDS.get(track.get("difficulty", "").lower())
        if field:
            summary[field] += 1
    return summary


def get_rate_price(rates):
    structured_rates = rates.get("rates", {})
    adult_day_rate = structured_rates.get("day-week", {}).get("adults")
    if adult_day_rate is not None:
        return parse_price(adult_day_rate)

    for item in structured_rates.get("items", []):
        name = item.get("name", "").lower()
        if "lift tickets" not in name or "adult" not in name or "4 hour lift" not in name:
            continue
        for price in item.get("prices", []):
            if price.get("label") == "price":
                return parse_price(price.get("value"))
    return None


def get_rental_price(rentals):
    structured_rentals = rentals.get("rentals", {})
    adult_price = structured_rentals.get("ski", {}).get("adults")
    if adult_price is not None:
        return parse_price(adult_price)

    for section in structured_rentals.get("sections", []):
        if "full day" not in section.get("name", "").lower():
            continue
        for item in section.get("items", []):
            if "adult" not in item.get("name", "").lower():
                continue
            for price in item.get("prices", []):
                if price.get("label") == "price":
                    return parse_price(price.get("value"))
    return None


def build_resort(static_info, rates, rentals, weather):
    resort = dict(static_info)
    resort["name"] = RESORT_NAME
    for field in ["hasAccommodations", "hasCrossCountry", "hasLessons", "hasSnowshoeing", "hasSpa", "hasTubing", "hasZipline"]:
        resort.setdefault(field, False)
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
    json_generators = directory / "json_generators"
    hours = load_json(json_generators / "hours-of-operation.json")
    rates = load_json(json_generators / "lift-rates.json")
    rentals = load_json(json_generators / "rentals.json")
    weather = load_json(json_generators / "tracks-and-lifts-weather-status.json")
    static_info = load_json(directory / "static_infos.json")
    return {"resortId": RESORT_ID, "tables": [
        {"table": "resorts", "content": build_resort(static_info, rates, rentals, weather)},
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
