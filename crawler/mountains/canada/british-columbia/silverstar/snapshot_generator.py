import json, re, subprocess, sys
from pathlib import Path

RESORT_ID = "silverstar"
RESORT_NAME = "SilverStar Mountain Resort"
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
    "double-black": "doubleBlack",
    "freestyle": "freeStyle",
    "free-style": "freeStyle",
    "green": "green",
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
        "dayTicketPrice",
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
        "lessonsPrice",
        "phone",
        "rating",
        "skiRentalPrice",
        "snowBoardRentalPrice",
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
        "ticketUrl",
        "tollFree",
        "tubbingPrice",
    ],
    "resortHours": ["resortId", "sourceUrl", "updatedAt", "hours"],
    "resortRates": ["resortId", "sourceUrl", "updatedAt", "rates"],
    "resortRentals": ["resortId", "sourceUrl", "updatedAt", "rentals"],
    "weatherAndStatus": ["resortId", "sourceUrl", "updatedAt", "lifts", "tracks"],
}


def load(path):
    with path.open("r", encoding="utf-8") as source:
        return json.load(source)


def price(value):
    match = re.search(r"\d[\d,.]*", str(value or ""))
    return None if not match else int(float(match.group().replace(",", "")))


def summary(weather):
    result = {"black": 0, "blue": 0, "doubleBlack": 0, "freeStyle": 0, "green": 0}
    for trail in weather.get("tracks", []):
        field = DIFFICULTY_FIELDS.get(str(trail.get("difficulty", "")).lower())
        if field:
            result[field] += 1
    return result


def build(static, rates, rentals, weather, ski):
    resort = {
        **static,
        "resortId": RESORT_ID,
        "name": RESORT_NAME,
        "tracksSummary": summary(weather),
    }
    for source, target in SKI_RESORT_FIELDS.items():
        if ski.get(source) not in (None, ""):
            resort[target] = ski[source]
    adult = price(rates.get("rates", {}).get("day-week", {}).get("adults"))
    if adult is not None:
        resort["dayTicketPrice"] = adult
    for kind, target in (
        ("ski", "skiRentalPrice"),
        ("snowboard", "snowBoardRentalPrice"),
    ):
        value = price(rentals.get("rentals", {}).get(kind, {}).get("adults"))
        if value is not None:
            resort[target] = value
    return resort


def run_generators(directory):
    generator = directory / "json_generators"
    for script in sorted(generator.glob("*.py")):
        subprocess.run([sys.executable, str(script)], cwd=generator, check=True)


def build_snapshot(directory=None):
    directory = Path(directory) if directory else Path(__file__).resolve().parent
    generator = directory / "json_generators"
    run_generators(directory)
    return {
        "resortId": RESORT_ID,
        "tables": [
            {
                "table": "resorts",
                "content": build(
                    load(directory / "static_infos.json"),
                    load(generator / "lift-rates.json"),
                    load(generator / "rentals.json"),
                    load(generator / "tracks-and-lifts-weather-status.json"),
                    load(generator / "skiresort.json"),
                ),
            },
            {
                "table": "resortHours",
                "content": load(generator / "hours-of-operation.json"),
            },
            {"table": "resortRates", "content": load(generator / "lift-rates.json")},
            {"table": "resortRentals", "content": load(generator / "rentals.json")},
            {
                "table": "weatherAndStatus",
                "content": load(generator / "tracks-and-lifts-weather-status.json"),
            },
        ],
    }


def report(snapshot, directory):
    tables = []
    count = 0
    for table in snapshot["tables"]:
        name = table["table"]
        missing = [
            column
            for column in TABLE_COLUMNS[name]
            if table["content"].get(column) in (None, "", [], {})
        ]
        count += len(missing)
        tables.append({"table": name, "missingColumns": missing})
    with (directory / "snapshot_generator_report.json").open(
        "w", encoding="utf-8"
    ) as output:
        json.dump(
            {"resortId": RESORT_ID, "tables": tables, "missingColumnCount": count},
            output,
            indent=2,
        )


def main():
    directory = Path(__file__).resolve().parent
    snapshot = build_snapshot(directory)
    with (directory / "snapshot_generator.json").open("w", encoding="utf-8") as output:
        json.dump(snapshot, output, indent=2)
    report(snapshot, directory)


if __name__ == "__main__":
    main()
