import json
import re
import subprocess
import sys
from pathlib import Path

RESORT_ID = "caledon-ski-club"
RESORT_NAME = "Caledon Ski Club"
DAY_TICKET_LABEL = "weekends & holidays"
ADULT_RENTAL_NAME = "adult"
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
        "conditions",
        "lifts",
        "liftsSummary",
        "trails",
        "trailsSummary",
        "terrainParks",
        "crossCountry",
        "tubing",
        "rawData",
    ],
}
DIFFICULTY_FIELDS = {
    "easy": "green",
    "medium": "blue",
    "hard": "black",
    "double black": "doubleBlack",
    "freestyle": "freeStyle",
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
    for trail in weather.get("trails", []):
        field = DIFFICULTY_FIELDS.get(trail.get("difficulty", "").lower())
        if field:
            summary[field] += 1
    return summary


def get_day_ticket_price(rates):
    for item in rates.get("rates", {}).get("items", []):
        if item.get("name", "").strip().lower() != "adult":
            continue
        for price in item.get("prices", []):
            if DAY_TICKET_LABEL not in price.get("label", "").lower():
                continue
            return parse_price(price.get("value"))
    return None


def get_rental_price(rentals, section_match, item_match, price_label):
    for section in rentals.get("rentals", {}).get("sections", []):
        if section_match not in section.get("name", "").lower():
            continue
        for item in section.get("items", []):
            if item_match not in item.get("name", "").lower():
                continue
            for price in item.get("prices", []):
                if price_label not in price.get("label", "").lower():
                    continue
                return parse_price(price.get("value"))
    return None


def build_resort(static_info, rates, rentals, weather):
    resort = dict(static_info)
    resort["name"] = RESORT_NAME
    resort.update(
        {
            "hasAccommodations": False,
            "hasCrossCountry": False,
            "hasSnowshoeing": False,
            "hasSpa": False,
            "hasTubing": False,
            "hasZipline": False,
            "hasLessons": False,
            "tracksSummary": build_tracks_summary(weather),
        }
    )
    prices = {
        "dayTicketPrice": get_day_ticket_price(rates),
        "skiRentalPrice": get_rental_price(
            rentals, "packages", ADULT_RENTAL_NAME, "full day"
        ),
    }
    prices["snowBoardRentalPrice"] = prices["skiRentalPrice"]
    for field, value in prices.items():
        if value is not None:
            resort[field] = value

    lessons_price = get_rental_price(rentals, "lesson", "", "cost")
    if lessons_price is not None:
        resort["lessonsPrice"] = lessons_price
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
    return {
        "resortId": RESORT_ID,
        "tables": [
            {
                "table": "resorts",
                "content": build_resort(
                    load_json(directory / "static_infos.json"),
                    load_json(json_generators / "lift-rates.json"),
                    load_json(json_generators / "rentals.json"),
                    load_json(json_generators / "weather-and-status.json"),
                ),
            },
            {
                "table": "resortHours",
                "content": load_json(json_generators / "hours-of-operation.json"),
            },
            {
                "table": "resortRates",
                "content": load_json(json_generators / "lift-rates.json"),
            },
            {
                "table": "resortRentals",
                "content": load_json(json_generators / "rentals.json"),
            },
            {
                "table": "weatherAndStatus",
                "content": load_json(json_generators / "weather-and-status.json"),
            },
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
