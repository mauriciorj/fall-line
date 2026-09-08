"""Snow Valley weather/status crawler."""

import json
import os
import re
import sys
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dtos import to_weather_dto

URL = "https://www.skisnowvalley.com/plan/weather-webcams/"
RESORT_ID = "snow-valley-ski-resort"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}


def get_trails_status():
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    data = {"snow_report": {}, "runs": [], "lifts": [], "tubing_zones": []}
    tables = soup.find_all("table")
    if tables:
        for row in tables[0].find_all("tr"):
            cells = row.find_all(["td", "th"])
            if len(cells) >= 2:
                data["snow_report"][cells[0].get_text(strip=True).lower().replace(" ", "_")] = cells[1].get_text(strip=True)
    for heading in soup.find_all(string=re.compile(r"^Runs$")):
        container = heading.find_parent()
        if not container:
            continue
        container = container.find_parent()
        parts = container.get_text("|", strip=True).split("|") if container else []
        for index, part in enumerate(parts):
            match = re.match(r"(\d+)/(\d+)\s*open", part, re.IGNORECASE)
            if not match:
                continue
            data["runs_summary"] = {"open": int(match.group(1)), "total": int(match.group(2))}
            for name in parts[index + 1:]:
                if name and not re.match(r"\d+/\d+", name):
                    data["runs"].append({"name": name, "status": "open"})
            break
        break
    for heading in soup.find_all(string=re.compile(r"^Lifts$")):
        container = heading.find_parent()
        container = container.find_parent() if container else None
        parts = container.get_text("|", strip=True).split("|") if container else []
        for index, part in enumerate(parts):
            match = re.match(r"(\d+)/(\d+)\s*open", part, re.IGNORECASE)
            if match:
                data["lifts_summary"] = {"open": int(match.group(1)), "total": int(match.group(2))}
                for name in parts[index + 1:]:
                    if name and not re.match(r"\d+/\d+", name):
                        data["lifts"].append({"name": name, "status": "open"})
                break
        break
    return data


def main():
    payload = {**to_weather_dto(get_trails_status()), "resortId": RESORT_ID, "sourceUrl": URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "weather-and-status.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
