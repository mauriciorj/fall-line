import json
import os
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

RESORT_ID = "antoine-mountain"
SOURCE_URL = "https://antoinemountain.ca/pages/trail-conditions"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}
DIFFICULTIES = {
    "voyageur": "green",
    "look out": "green",
    "static": "green",
    "nice 'n' easy": "green",
    "portage": "green",
    "handle tow": "green",
    "mattawa": "blue",
    "ottawa": "blue",
    "dambuster": "blue",
    "laurentian": "blue",
    "bowl": "blue",
    "kate pace": "black",
    "chute": "black",
    "cliffhanger": "doubleBlack",
    "spillway": "doubleBlack",
}
DIFFICULTY_IMAGES = {
    "easy.png": "green",
    "square.png": "blue",
    "double-diamond.png": "doubleBlack",
    "diamond.png": "black",
}


def normalize_text(value):
    return " ".join(value.lower().split())


def normalize_status(value):
    status = normalize_text(value)
    if "open" in status:
        return "open"
    if "closed" in status:
        return "closed"
    return status


def parse_difficulty(name, cell):
    image = cell.find("img")
    source = image.get("src", "").lower() if image else ""
    for marker, difficulty in DIFFICULTY_IMAGES.items():
        if marker in source:
            return difficulty
    return DIFFICULTIES.get(normalize_text(name))


def get_status():
    response = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.select_one("table.hours")
    if not table:
        raise ValueError("Could not find Antoine trail conditions table")
    tracks = []
    for row in table.find_all("tr")[1:]:
        cells = row.find_all("td")
        if len(cells) < 3:
            continue
        name = cells[0].get_text(" ", strip=True)
        if not name:
            continue
        tracks.append({
            "name": name,
            "status": normalize_status(cells[1].get_text(" ", strip=True)),
            "difficulty": parse_difficulty(name, cells[2]),
        })
    if not tracks:
        raise ValueError("No Antoine trail status rows found")
    return {"lifts": [], "tracks": tracks, "terrainParks": []}


def main():
    payload = {
        **get_status(),
        "resortId": RESORT_ID,
        "sourceUrl": SOURCE_URL,
        "updatedAt": int(time.time() * 1000),
    }
    output_file = os.path.join(
        os.path.dirname(__file__), "tracks-and-lifts-weather-status.json"
    )
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
