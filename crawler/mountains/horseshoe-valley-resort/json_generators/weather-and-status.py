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

URL = "https://horseshoeresort.com/ski-report-trails/"
RESORT_ID = "horseshoe-valley-resort"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def get_trail_status():
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    data = {
        "conditions": {},
        "runs": {"easy": [], "difficult": [], "more_difficult": [], "terrain_park": []},
        "lifts": [],
        "cross_country": [],
        "tube_park": {},
    }
    text = soup.get_text("|", strip=True)
    for key, pattern in {
        "hours": r"Hours\|([^|]+)",
        "surface_conditions": r"Conditions\|([^|]+)",
        "base_depth": r"Base Depth\|([^|]+)",
    }.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data["conditions"][key] = match.group(1).strip()
    snowfall = re.search(r"(\d+)\s*\|?\s*cm", text, re.IGNORECASE)
    if snowfall:
        data["conditions"]["snowfall_24h"] = f"{snowfall.group(1)} cm"

    difficulty_map = {
        "easy": "easy",
        "difficult": "difficult",
        "more difficult": "more_difficult",
        "terrain park": "terrain_park",
    }
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if not rows:
            continue
        headers = [cell.get_text(" ", strip=True) for cell in rows[0].find_all(["th", "td"])]
        header_text = " ".join(headers).lower()
        if "trail" in header_text and "distance" in header_text:
            for row in rows[1:]:
                cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["td", "th"])]
                if len(cells) >= 5:
                    data["cross_country"].append({"trail": cells[0], "distance": cells[1], "open": cells[2], "track_set": cells[3], "groomed_today": cells[4]})
            continue
        if any(key in header_text for key in ["lift", "chair", "carpet"]):
            for row in rows[1:]:
                cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["td", "th"])]
                if len(cells) >= 3:
                    data["lifts"].append({"name": cells[0], "day_status": cells[1], "night_status": cells[2]})
            continue
        category = next((value for key, value in difficulty_map.items() if key in header_text), None)
        if category:
            for row in rows[1:]:
                cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["td", "th"])]
                if len(cells) >= 3:
                    data["runs"][category].append({"name": cells[0], "day_status": cells[1], "night_status": cells[2]})
    return data


def main():
    payload = {
        **to_weather_dto(get_trail_status()),
        "resortId": RESORT_ID,
        "sourceUrl": URL,
        "updatedAt": int(time.time() * 1000),
    }
    output_file = os.path.join(os.path.dirname(__file__), "weather-and-status.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
