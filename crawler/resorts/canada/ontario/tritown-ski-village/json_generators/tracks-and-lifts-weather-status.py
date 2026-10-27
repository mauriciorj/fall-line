import json
import os
import time
import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

PAGE_URL = "https://tritownskivillage.ca/"
RESORT_ID = "tritown-ski-village"
TRACKS = {
    "Skiers Grant": "green",
    "Richelieu": "green",
    "Frogs Breath Pass": "green",
    "Whistler": "blue",
    "Expresso": "blue",
    "Jaws": "black",
    "Down Draft": "black",
    "Kool Kate": "green",
    "True Grit": "blue",
    "Zoot": "black",
    "Donkey Trail": "green",
    "Big G": "blue",
    "Willar's Way": "blue",
    "Half Way": "blue",
    "Bunny Run": "green",
}


def get_status():
    response = requests.get(PAGE_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    response.raise_for_status()
    text = BeautifulSoup(response.content, "html.parser").get_text(" ", strip=True).lower()
    if "green" not in text or "black" not in text:
        raise ValueError("Could not verify trail HTML")
    return {
        "lifts": [
            {"name": "T Bar", "status": "not informed"},
            {"name": "Handle Tow", "status": "not informed"},
        ],
        "tracks": [
            {"name": name, "status": "not informed", "difficulty": difficulty}
            for name, difficulty in TRACKS.items()
        ],
        "terrainParks": [],
    }


def main():
    payload = {**get_status(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    with open(os.path.join(os.path.dirname(__file__), "tracks-and-lifts-weather-status.json"), "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
