import json
import os
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

PAGE_URL = "https://www.batawaskihill.com/"
RESORT_ID = "batawa-ski-hill"
HEADERS = {"User-Agent": "Mozilla/5.0"}
TRACKS = {
    "Bambi": "green",
    "Boomerang": "green",
    "Long John": "blue",
    "Detour": "blue",
    "Meadow": "blue",
    "Easy Way": "blue",
    "Lightning": "blue",
    "The Chute": "blue",
    "Gus' Chili Bowl": "black",
    "Smokey": "black",
    "Reneglade": "doubleBlack",
    "Old Smokey": "doubleBlack",
    "The Factory": "freeStyle",
}


def get_status():
    response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    text = BeautifulSoup(response.content, "html.parser").get_text(" ", strip=True).lower()
    if "trail" not in text and "ski hill" not in text:
        raise ValueError("Could not verify trail HTML")
    return {
        "lifts": [],
        "tracks": [
            {"name": name, "status": "not informed", "difficulty": difficulty}
            for name, difficulty in TRACKS.items()
            if name != "The Factory"
        ],
        "terrainParks": [
            {"name": "The Factory", "status": "not informed", "difficulty": "freeStyle"}
        ],
    }


def main():
    payload = {
        **get_status(),
        "resortId": RESORT_ID,
        "sourceUrl": PAGE_URL,
        "updatedAt": int(time.time() * 1000),
    }
    output_file = os.path.join(os.path.dirname(__file__), "tracks-and-lifts-weather-status.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
