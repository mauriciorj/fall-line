import json
import os
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

PAGE_URL = "https://www.skikenora.ca/downhill/"
RESORT_ID = "ski-kenora"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}
LIFTS = ("Colin Myles", "Skyline", "Magic Carpet")
TRACK_DIFFICULTIES = {
    "Gentle Ben": "green",
    "Bunny Slope": "blue",
    "Otter Slide": "blue",
    "Chicken Trail": "green",
    "Lover’s Lane": "green",
    "Sidewinder": "green",
    "Surprise": "blue",
    "Pete’s Fancy": "black",
    "Skyline": "black",
    "B-Slalom": "black",
    "Mary Glen": "green",
    "Shortcut": "black",
    "Rotary Learn to Ski Area": "green",
    "Terrain Park": "blue",
}


def normalize_text(value):
    return " ".join(value.replace("’", "'").split()).lower()


def get_status():
    response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    statuses = {}
    for row in soup.find_all("tr"):
        cells = row.find_all(["th", "td"])
        if len(cells) < 2:
            continue
        name = normalize_text(cells[0].get_text(" ", strip=True))
        status = normalize_text(cells[-1].get_text(" ", strip=True))
        if status in {"open", "closed", "not available"}:
            statuses[name] = status

    missing = [name for name in (*LIFTS, *TRACK_DIFFICULTIES) if normalize_text(name) not in statuses]
    if missing:
        raise ValueError(f"Missing hill condition statuses: {missing}")

    return {
        "lifts": [{"name": name, "status": statuses[normalize_text(name)]} for name in LIFTS],
        "tracks": [
            {"name": name, "status": statuses[normalize_text(name)], "difficulty": difficulty}
            for name, difficulty in TRACK_DIFFICULTIES.items()
        ],
        "terrainParks": [],
    }


def main():
    payload = {"resortId": RESORT_ID, **get_status(), "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "tracks-and-lifts-weather-status.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
