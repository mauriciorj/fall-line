import json
import re
import subprocess
import sys
from pathlib import Path

RESORT_ID = "sun-peaks-resort"
RESORT_NAME = "Sun Peaks Resort"
SKI_RESORT_FIELDS = {"elevation":"elevation","height":"height","tracks-green-length":"tracksGreenLength","tracks-green-proportion":"tracksGreenProportion","tracks-blue-length":"tracksBlueLength","tracks-blue-proportion":"tracksBlueProportion","tracks-black-length":"tracksBlackLength","tracks-black-proportion":"tracksBlackProportion","tracks-total-length":"tracksTotalLength"}
DIFFICULTY_FIELDS = {"easy":"green","medium":"blue","hard":"black","black":"black","blue":"blue","doubleblack":"doubleBlack","double black":"doubleBlack","double-black":"doubleBlack","freestyle":"freeStyle","free style":"freeStyle","free-style":"freeStyle","green":"green"}
TABLE_COLUMNS = {
    "resorts": ["resortId","published","name","continent","country","region","website","address","coordinates","dayTicketPrice","email","googleMapsUrl","hasIceSkate","hasAccommodations","hasCrossCountry","hasLessons","hasSnowshoeing","hasSpa","hasTubing","hasZipline","lessonsPrice","phone","rating","skiRentalPrice","snowBoardRentalPrice","tracksSummary","elevation","height","tracksGreenLength","tracksGreenProportion","tracksBlueLength","tracksBlueProportion","tracksBlackLength","tracksBlackProportion","tracksTotalLength","ticketUrl","tollFree","tubbingPrice"],
    "resortHours":["resortId","sourceUrl","updatedAt","hours"],"resortRates":["resortId","sourceUrl","updatedAt","rates"],"resortRentals":["resortId","sourceUrl","updatedAt","rentals"],"weatherAndStatus":["resortId","sourceUrl","updatedAt","lifts","tracks"],
}


def load_json(path):
    with path.open("r", encoding="utf-8") as source:
        return json.load(source)


def parse_price(value):
    match = re.search(r"\d[\d,.]*", str(value or ""))
    if not match:
        return None
    amount = float(match.group().replace(",", ""))
    return int(amount) if amount.is_integer() else amount


def build_tracks_summary(weather):
    summary = {"black":0,"blue":0,"doubleBlack":0,"freeStyle":0,"green":0}
    for trail in weather.get("tracks", []) + weather.get("terrainParks", []):
        field = DIFFICULTY_FIELDS.get(str(trail.get("difficulty", "")).strip().lower())
        if field:
            summary[field] += 1
    return summary


def get_day_ticket_price(rates):
    return parse_price(rates.get("rates", {}).get("day-week", {}).get("adults"))


def get_rental_price(rentals, rental_type):
    return parse_price(rentals.get("rentals", {}).get(rental_type, {}).get("adults"))


def build_resort(static_info, rates, rentals, weather, ski_resort_info):
    resort = {**static_info, "resortId": RESORT_ID, "name": RESORT_NAME}
    for source_field, resort_field in SKI_RESORT_FIELDS.items():
        value = ski_resort_info.get(source_field)
        if value not in (None, ""):
            resort[resort_field] = value
    resort["tracksSummary"] = build_tracks_summary(weather)
    day_price = get_day_ticket_price(rates)
    if day_price is not None:
        resort["dayTicketPrice"] = day_price
    for rental_type, field in (("ski", "skiRentalPrice"), ("snowboard", "snowBoardRentalPrice")):
        price = get_rental_price(rentals, rental_type)
        if price is not None:
            resort[field] = price
    return resort


def run_json_generators(directory):
    generator_dir = directory / "json_generators"
    for script in sorted(generator_dir.glob("*.py")):
        subprocess.run([sys.executable, str(script)], cwd=generator_dir, check=True)


def build_snapshot(directory=None):
    directory = Path(directory) if directory is not None else Path(__file__).resolve().parent
    run_json_generators(directory)
    generator_dir = directory / "json_generators"
    return {"resortId": RESORT_ID, "tables": [
        {"table":"resorts","content":build_resort(load_json(directory/"static_infos.json"), load_json(generator_dir/"lift-rates.json"), load_json(generator_dir/"rentals.json"), load_json(generator_dir/"tracks-and-lifts-weather-status.json"), load_json(generator_dir/"skiresort.json"))},
        {"table":"resortHours","content":load_json(generator_dir/"hours-of-operation.json")}, {"table":"resortRates","content":load_json(generator_dir/"lift-rates.json")}, {"table":"resortRentals","content":load_json(generator_dir/"rentals.json")}, {"table":"weatherAndStatus","content":load_json(generator_dir/"tracks-and-lifts-weather-status.json")},
    ]}


def generate_report(snapshot, directory=None):
    directory = Path(directory) if directory is not None else Path(__file__).resolve().parent
    tables=[]; count=0
    for table in snapshot["tables"]:
        name=table["table"]; missing=[column for column in TABLE_COLUMNS[name] if table.get("content",{}).get(column) in (None,"",[],{})]; count += len(missing); tables.append({"table":name,"missingColumns":missing})
    report={"resortId":snapshot["resortId"],"tables":tables,"missingColumnCount":count}
    with (directory/"snapshot_generator_report.json").open("w",encoding="utf-8") as output: json.dump(report,output,indent=2,ensure_ascii=False)
    return report


def main():
    directory=Path(__file__).resolve().parent; snapshot=build_snapshot(directory)
    with (directory/"snapshot_generator.json").open("w",encoding="utf-8") as output: json.dump(snapshot,output,indent=2,ensure_ascii=False)
    generate_report(snapshot,directory)


if __name__ == "__main__":
    main()
