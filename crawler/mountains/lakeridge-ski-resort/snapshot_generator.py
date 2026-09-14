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
        "skiRentalPrice", "snowBoardRentalPrice", "tracksSummary", "elevation", "height",
        "tracksGreenLength", "tracksGreenProportion", "tracksBlueLength",
        "tracksBlueProportion", "tracksBlackLength", "tracksBlackProportion",
        "tracksTotalLength", "ticketUrl",
        "tollFree", "tubbingPrice",
    ],
    "resortHours": ["resortId", "sourceUrl", "updatedAt", "hours"],
    "resortRates": ["resortId", "sourceUrl", "updatedAt", "rates"],
    "resortRentals": ["resortId", "sourceUrl", "updatedAt", "rentals"],
    "weatherAndStatus": [
        "resortId", "sourceUrl", "updatedAt", "tracks",
    ],
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
    "doubleblack": "doubleBlack",
    "double black": "doubleBlack",
    "blue": "blue",
    "green": "green",
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
    for trail in weather.get("tracks", []):
        difficulty = trail.get("difficulty", "").lower()
        field = DIFFICULTY_FIELDS.get(difficulty)
        if field:
            summary[field] += 1
    return summary


def get_rate_price(rates, section_match, price_label):
    structured_rates = rates.get("rates", {})
    adult_day_rate = structured_rates.get("day-week", {}).get("adults")
    if adult_day_rate is not None:
        return parse_price(adult_day_rate)

    for item in structured_rates.get("items", []):
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
    structured_rentals = rentals.get("rentals", {})
    if "snowboard" in section_match:
        value = structured_rentals.get("snowboard", {}).get("adults")
    else:
        value = structured_rentals.get("ski", {}).get("adults")
    if value is not None:
        return parse_price(value)

    for section in structured_rentals.get("sections", []):
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


def build_resort(static_info, rates, rentals, weather, ski_resort_info=None):
    resort = dict(static_info)
    resort["name"] = RESORT_NAME
    for source_field, resort_field in SKI_RESORT_FIELDS.items():
        value = (ski_resort_info or {}).get(source_field)
        if value not in (None, ""):
            resort[resort_field] = value
    resort["hasAccommodations"] = bool(static_info.get("resort_accommodations"))
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
            {"table": "resorts", "content": build_resort(static_info, rates, rentals, weather, ski_resort_info)},
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
