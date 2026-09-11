import json
import re
import subprocess
import sys
from pathlib import Path

RESORT_ID = "blue-mountain"
RESORT_NAME = "Blue Mountain"
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
        "dayTicketPrice",
        "email",
        "googleMapsUrl",
        "hasAccommodations",
        "hasCrossCountry",
        "hasLessons",
        "hasSnowshoeing",
        "hasSpa",
        "hasTubing",
        "hasZipline",
        "lessonsPrice",
        "phone",
        "rating",
        "skiRentalPrice",
        "snowBoardRentalPrice",
        "tracksSummary",
        "ticketUrl",
        "tollFree",
        "tubbingPrice",
    ],
    "resortHours": ["resortId", "sourceUrl", "updatedAt", "hours"],
    "resortRates": ["resortId", "sourceUrl", "updatedAt", "rates"],
    "resortRentals": ["resortId", "sourceUrl", "updatedAt", "rentals"],
    "weatherAndStatus": [
        "resortId",
        "sourceUrl",
        "updatedAt",
        "lifts",
        "trails",
        "terrainParks",
        "crossCountry",
        "tubing",
        "rawData",
    ],
}
DIFFICULTY_FIELDS = {
    "black": "black",
    "black diamond": "black",
    "blue": "blue",
    "blue square": "blue",
    "double-black": "doubleBlack",
    "double black": "doubleBlack",
    "double black diamond": "doubleBlack",
    "free-style": "freeStyle",
    "freestyle": "freeStyle",
    "free style": "freeStyle",
    "green": "green",
    "green circle": "green",
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
    summary = {
        "black": 0,
        "blue": 0,
        "doubleBlack": 0,
        "freeStyle": 0,
        "green": 0,
    }
    for trail in weather.get("trails", []) + weather.get("terrainParks", []):
        field = DIFFICULTY_FIELDS.get(trail.get("difficulty", "").lower())
        if field:
            summary[field] += 1
    return summary


def get_day_ticket_price(rates):
    for item in rates.get("rates", {}).get("items", []):
        if "adult" not in item.get("name", "").lower():
            continue
        for price in item.get("prices", []):
            value = parse_price(price.get("value"))
            if value is not None:
                return value
    return None


def get_rental_price(rentals, section_match, item_match):
    for section in rentals.get("rentals", {}).get("sections", []):
        if section_match not in section.get("name", "").lower():
            continue
        for item in section.get("items", []):
            if item_match not in item.get("name", "").lower():
                continue
            for price in item.get("prices", []):
                label = price.get("label", "").lower()
                if label not in {"price", "cost", "rate", "amount"} and "price" not in label:
                    continue
                value = parse_price(price.get("value"))
                if value is not None:
                    return value
    return None


def build_resort(static_info, rates, rentals, weather):
    resort = dict(static_info)
    resort["name"] = RESORT_NAME
    for field in [
        "hasAccommodations",
        "hasCrossCountry",
        "hasLessons",
        "hasSnowshoeing",
        "hasSpa",
        "hasTubing",
        "hasZipline",
    ]:
        resort.setdefault(field, False)
    resort["tracksSummary"] = build_tracks_summary(weather)

    prices = {
        "dayTicketPrice": get_day_ticket_price(rates),
        "skiRentalPrice": get_rental_price(rentals, "adult_ski", "adult ski"),
        "snowBoardRentalPrice": get_rental_price(
            rentals, "adult_snowboard", "adult snowboard"
        ),
    }
    for field, value in prices.items():
        if value is not None:
            resort[field] = value
    return resort


def run_json_generators(directory):
    json_generators = directory / "json_generators"
    for script in sorted(json_generators.glob("*.py")):
        subprocess.run(
            [sys.executable, str(script)],
            cwd=json_generators,
            check=True,
        )


def build_snapshot(directory=None):
    directory = (
        Path(directory) if directory is not None else Path(__file__).resolve().parent
    )
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
    directory = (
        Path(directory) if directory is not None else Path(__file__).resolve().parent
    )
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
