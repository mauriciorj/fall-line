import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.mountdufour.com/"
PAGE_URL = "https://www.mountdufour.com/index.php/the-mountain/ski-conditions"
RESORT_ID = "mount-dufour"
LIFTS = ("Quad Lift", "Beginner Poma Lift")
TRACK_DIFFICULTIES = {
    "Beginner's Trail": "green",
    "Bruno's Edge": "black",
    "Dengg's Peak": "black",
    "Family Trail": "green",
    "Idiot's Delight": "black",
    "Main Run": "blue",
    "Valley Trail": "green",
}
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


def normalize_text(value):
    return " ".join(value.replace("\xa0", " ").split()).lower()


def get_status():
    response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    text = normalize_text(BeautifulSoup(response.content, "html.parser").get_text(" ", strip=True))
    statuses = {}
    for name in (*LIFTS, *TRACK_DIFFICULTIES, "Terrain Park"):
        if name == "Terrain Park":
            match = re.search(r"terrain park\s*/\s*(open|closed)", text, re.IGNORECASE)
        else:
            match = re.search(rf"{re.escape(name.lower())}\s+(open|closed|not available)", text, re.IGNORECASE)
        if not match:
            raise ValueError(f"Could not find HTML status for {name}")
        statuses[name] = match.group(1).lower()
    return {
        "lifts": [{"name": name, "status": statuses[name]} for name in LIFTS],
        "tracks": [
            {"name": name, "status": statuses[name], "difficulty": difficulty}
            for name, difficulty in TRACK_DIFFICULTIES.items()
        ],
        "terrainParks": [{"name": "Terrain Park", "status": statuses["Terrain Park"], "difficulty": "freeStyle"}],
    }


def main():
    payload = {**get_status(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "tracks-and-lifts-weather-status.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
