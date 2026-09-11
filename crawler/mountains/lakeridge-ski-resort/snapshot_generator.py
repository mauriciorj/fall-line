import json
import re
import subprocess
import sys
from pathlib import Path

RESORT_ID = "lakeridge-ski-resort"
RESORT_NAME = "Lakeridge Ski Resort"
TABLE_COLUMNS = {
    "resorts": [
        "resortId", "published", "name", "continent", "country", "region", "website",
        "address", "coordinates", "dayTicketPrice", "email", "googleMapsUrl",
        "hasAccommodations", "hasCrossCountry", "hasLessons", "hasSnowshoeing",
        "hasSpa", "hasTubing", "hasZipline", "lessonsPrice", "phone", "rating",
        "skiRentalPrice", "snowBoardRentalPrice", "tracksSummary", "ticketUrl",
        "tollFree", "tubbingPrice",
    ],
    "resortHours": ["resortId", "sourceUrl", "updatedAt", "hours"],
    "resortRates": ["resortId", "sourceUrl", "updatedAt", "rates"],
    "resortRentals": ["resortId", "sourceUrl", "updatedAt", "rentals"],
    "weatherAndStatus": [
        "resortId", "sourceUrl", "updatedAt", "lifts", "trails", "terrainParks",
        "crossCountry", "tubing", "rawData",
    ],
}
DIFFICULTY_FIELDS = {
    "black diamond": "black",
    "double black diamond": "doubleBlack",
    "blue square": "blue",
    "green circle": "green",
    "orange oval": "freeStyle",
    "free style": "freeStyle",
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
    for trail in weather.get("trails", []) + weather.get("terrainParks", []):
        difficulty = trail.get("difficulty", "").lower()
        field = DIFFICULTY_FIELDS.get(difficulty)
        if field:
            summary[field] += 1
    return summary


def get_rate_price(rates, section_match, price_label):
    for item in rates.get("rates", {}).get("items", []):
        name = item.get("name", "").lower()
        if section_match not in name:
            continue
        for price in item.get("prices", []):
            if price_label in price.get("label", "").lower():
                return parse_price(price.get("value"))
    return None


def get_rental_price(rentals, section_match, item_match, label_match):
    for section in rentals.get("rentals", {}).get("sections", []):
        section_name = " ".join(section.get("name", "").lower().split())
        if section_match not in section_name:
            continue
        for item in section.get("items", []):
            if item_match not in item.get("name", "").lower():
                continue
            for price in item.get("prices", []):
                if label_match in price.get("label", "").lower():
                    return parse_price(price.get("value"))
    return None


def get_first_rental_price(rentals, section_match, item_match):
    for section in rentals.get("rentals", {}).get("sections", []):
        section_name = " ".join(section.get("name", "").lower().split())
        if section_match not in section_name:
            continue
        for item in section.get("items", []):
            if item_match not in item.get("name", "").lower():
                continue
            prices = item.get("prices", [])
            if prices:
                return parse_price(prices[0].get("value"))
    return None


def build_resort(static_info, rates, rentals, weather):
    resort = dict(static_info)
    resort["name"] = RESORT_NAME
    for field in [
        "hasAccommodations", "hasCrossCountry", "hasLessons", "hasSnowshoeing",
        "hasSpa", "hasTubing", "hasZipline",
    ]:
        resort.setdefault(field, False)
    resort["tracksSummary"] = build_tracks_summary(weather)

    prices = {
        "dayTicketPrice": get_rate_price(rates, "thursday to sunday lift tickets", "adult"),
        "skiRentalPrice": get_first_rental_price(rentals, "skis, boots and poles", "adult"),
        "snowBoardRentalPrice": get_first_rental_price(rentals, "snowboard and boots package", "adult"),
        "lessonsPrice": get_rental_price(rentals, "rental packages for lessons", "7 week package", "ski"),
    }
    for field, value in prices.items():
        if value is not None:
            resort[field] = value
    if prices["lessonsPrice"] is not None:
        resort["hasLessons"] = True
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
    weather = load_json(json_generators / "weather-and-status.json")
    static_info = load_json(directory / "static_infos.json")
    return {
        "resortId": RESORT_ID,
        "tables": [
            {"table": "resorts", "content": build_resort(static_info, rates, rentals, weather)},
            {"table": "resortHours", "content": hours},
            {"table": "resortRates", "content": rates},
            {"table": "resortRentals", "content": rentals},
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
            column for column in TABLE_COLUMNS[table_name]
            if not has_value(table.get("content", {}), column)
        ]
        missing_column_count += len(missing_columns)
        tables.append({"table": table_name, "missingColumns": missing_columns})
    report = {
        "resortId": snapshot["resortId"],
        "tables": tables,
        "missingColumnCount": missing_column_count,
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
