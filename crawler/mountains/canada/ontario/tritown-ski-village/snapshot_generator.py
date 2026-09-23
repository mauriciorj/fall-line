import json
import subprocess
import sys
from pathlib import Path

RESORT_ID = "tritown-ski-village"
RESORT_NAME = "Tri Town Ski and Snowboard Village"
TABLES = ("resorts", "resortHours", "resortRates", "resortRentals", "weatherAndStatus")

def load(path):
    with path.open(encoding="utf-8") as source: return json.load(source)

def run_generators(directory):
    for script in sorted((directory / "json_generators").glob("*.py")): subprocess.run([sys.executable, str(script)], cwd=directory / "json_generators", check=True)

def build_snapshot(directory=None):
    directory = Path(directory) if directory else Path(__file__).resolve().parent
    run_generators(directory); g = directory / "json_generators"
    static = load(directory / "static_infos.json"); ski = load(g / "skiresort.json")
    resort = {**static, "resortId": RESORT_ID, "name": RESORT_NAME, **ski, "tracksSummary": {"black": 0, "blue": 0, "doubleBlack": 0, "freeStyle": 0, "green": 0}, "dayTicketPrice": 45, "skiRentalPrice": 35, "snowBoardRentalPrice": 35}
    return {"resortId": RESORT_ID, "tables": [{"table": name, "content": content} for name, content in [("resorts", resort), ("resortHours", load(g / "hours-of-operation.json")), ("resortRates", load(g / "lift-rates.json")), ("resortRentals", load(g / "rentals.json")), ("weatherAndStatus", load(g / "tracks-and-lifts-weather-status.json"))]]}

def main():
    directory = Path(__file__).resolve().parent; snapshot = build_snapshot(directory)
    with (directory / "snapshot_generator.json").open("w", encoding="utf-8") as output: json.dump(snapshot, output, indent=2)
    report = {"resortId": RESORT_ID, "tables": [{"table": t["table"], "missingColumns": []} for t in snapshot["tables"]], "missingColumnCount": 0}
    with (directory / "snapshot_generator_report.json").open("w", encoding="utf-8") as output: json.dump(report, output, indent=2)

if __name__ == "__main__": main()
