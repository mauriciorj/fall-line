import json
import os
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://searchmont.com/"
PAGE_URL = "https://searchmont.com/snow-report/"
RESORT_ID = "searchmont"
LIFTS = ("Lumberjack Belt", "Wabos Belt", "Buzzsaw Lift", "Goulais Lift", "Main Lift")
TRACKS = (
    "Binder Twine", "Champs", "Goulais", "Meadow Express", "Nan's Ski Askin",
    "Peggy's Promise", "Really Mealey", "Rocky Road", "3X4", "Buzzsaw",
    "Herb's Meadow", "Learning Centre", "Little Wabos", "Lumberjack", "The Main",
    "Trav's Trail", "5-0 Trees", "Agawa", "Bear Claw", "Brian's Brook", "Cougar Trax",
    "Exhibition Alley", "Jack's Dive", "Melville's Mile", "Moose Difficult", "Slalom",
    "The Glades", "Wolf's Head",
)
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


def normalize_status(value):
    value = " ".join(value.lower().split())
    return "open" if "open" in value else "closed" if "closed" in value else value


def get_status():
    statuses = {}
    try:
        response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        text = " ".join(soup.get_text(" ", strip=True).split())
        for name in (*LIFTS, *TRACKS, "Terrain Park"):
            marker = f"{name}:"
            start = text.lower().find(marker.lower())
            if start >= 0:
                statuses[name] = normalize_status(text[start + len(marker):start + len(marker) + 20])
    except requests.RequestException:
        pass
    return {
        "lifts": [{"name": name, "status": statuses.get(name, "closed")} for name in LIFTS],
        "tracks": [{"name": name, "status": statuses.get(name, "closed")} for name in TRACKS],
        "terrainParks": [{"name": "Terrain Park", "status": statuses.get("Terrain Park", "closed"), "difficulty": "freeStyle"}],
    }


def main():
    payload = {**get_status(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "tracks-and-lifts-weather-status.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
