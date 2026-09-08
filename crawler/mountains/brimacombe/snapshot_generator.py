import json
import subprocess
import sys
from pathlib import Path

RESORT_ID = "brimacombe"
RESORT_NAME = "Brimacombe"
DAY_TICKET_PRICE_LABEL = "Friday to Sunday & Holidays Valid up to 4 Hours"
LESSON_RENTAL_NAME = "7-Week Snow School Program Ski or Snowboard Rental Package (Skis, Boots and Poles or Snowboard and Boots)"
ADULT_RENTAL_NAME = "(Ages 14+ ) Ski or Snowboard Package"
TABLE_COLUMNS = {
    "resorts": [
        "resortId",
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


def build_tracks_summary(weather):
    summary = {
        "black": 0,
        "blue": 0,
        "doubleBlack": 0,
        "freeStyle": 0,
        "green": 0,
    }
    for trail in weather.get("trails", []):
        field = DIFFICULTY_FIELDS.get(trail.get("difficulty", "").lower())
        if field:
            summary[field] += 1
    return summary


def get_day_ticket_price(rates):
    for item in rates.get("rates", {}).get("items", []):
        if item.get("name") != "Adult (18+)":
            continue
        for price in item.get("prices", []):
            if price.get("label") != DAY_TICKET_PRICE_LABEL:
                continue
            value = price.get("value", "").replace("$", "").replace(",", "").strip()
            if not value:
                return None
            amount = float(value)
            return int(amount) if amount.is_integer() else amount
    return None


def get_rental_price(rentals, section_name, item_name):
    for section in rentals.get("rentals", {}).get("sections", []):
        if section.get("name") != section_name:
            continue
        for item in section.get("items", []):
            if item.get("name") != item_name:
                continue
            for price in item.get("prices", []):
                if price.get("label") != "Cost":
                    continue
                value = price.get("value", "").replace("$", "").replace(",", "").strip()
                if not value:
                    return None
                amount = float(value)
                return int(amount) if amount.is_integer() else amount
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
        }
    )
    resort["tracksSummary"] = build_tracks_summary(weather)
    prices = {
        "dayTicketPrice": get_day_ticket_price(rates),
        "lessonsPrice": get_rental_price(
            rentals, "7-Week Program Lesson Rentals", LESSON_RENTAL_NAME
        ),
        "skiRentalPrice": get_rental_price(
            rentals, "Individual Rental Packages", ADULT_RENTAL_NAME
        ),
        "snowBoardRentalPrice": get_rental_price(
            rentals, "Individual Rental Packages", ADULT_RENTAL_NAME
        ),
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
            {
                "table": "resorts",
                "content": build_resort(static_info, rates, rentals, weather),
            },
            {
                "table": "resortHours",
                "content": hours,
            },
            {
                "table": "resortRates",
                "content": rates,
            },
            {
                "table": "resortRentals",
                "content": rentals,
            },
            {
                "table": "weatherAndStatus",
                "content": weather,
            },
        ],
    }


def has_value(content, column):
    if column not in content:
        return False
    value = content[column]
    return value not in (None, "", [], {})


def generate_report(snapshot, directory=None):
    directory = (
        Path(directory) if directory is not None else Path(__file__).resolve().parent
    )
    tables = []
    missing_column_count = 0
    for table in snapshot["tables"]:
        table_name = table["table"]
        content = table.get("content", {})
        missing_columns = [
            column
            for column in TABLE_COLUMNS[table_name]
            if not has_value(content, column)
        ]
        missing_column_count += len(missing_columns)
        tables.append(
            {
                "table": table_name,
                "missingColumns": missing_columns,
            }
        )

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
