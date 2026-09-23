import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.devilsglen.com"
PAGE_URL = f"{SOURCE_URL}/About/Trail_Report"
RESORT_ID = "devils-glen"
EXPECTED_COUNTS = {"tracks": 21, "lifts": 4, "terrainParks": 3}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}
DIFFICULTY_NAMES = {
    "green": "green",
    "blue": "blue",
    "black": "black",
    "group_1": "black",
    "orange": "freeStyle",
}


def fetch_soup():
    response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser")


def normalize_text(value):
    return " ".join(value.lower().split())


def parse_difficulty(cell):
    image = cell.find("img")
    if not image:
        return None
    source = normalize_text(image.get("src", ""))
    for name, difficulty in DIFFICULTY_NAMES.items():
        if f"/{name}.aspx" in source:
            return difficulty
    return None


def normalize_status(value):
    normalized = normalize_text(value)
    if "open" in normalized:
        return "open"
    if "closed" in normalized:
        return "closed"
    return normalized


def parse_tracks(table):
    tracks = []
    for row in table.find_all("tr")[1:]:
        cells = row.find_all("td")
        if len(cells) < 3:
            continue
        name = cells[0].get_text(" ", strip=True)
        status = normalize_status(cells[2].get_text(" ", strip=True))
        if name and status:
            tracks.append(
                {
                    "difficulty": parse_difficulty(cells[1]),
                    "name": name,
                    "status": status,
                }
            )
    return tracks


def parse_lifts(table):
    lifts = []
    for row in table.find_all("tr")[1:]:
        cells = row.find_all("td")
        if len(cells) < 2:
            continue
        name = cells[0].get_text(" ", strip=True)
        status = normalize_status(cells[1].get_text(" ", strip=True))
        if name and status:
            lifts.append({"name": name, "status": status})
    return lifts


def get_status():
    tables = fetch_soup().find_all("table")
    if len(tables) < 2:
        raise ValueError("Could not find Devil's Glen trail and lift tables")
    all_tracks = parse_tracks(tables[0])
    lifts = parse_lifts(tables[1])
    terrain_parks = [track for track in all_tracks if track.get("difficulty") == "freeStyle"]
    tracks = [track for track in all_tracks if track.get("difficulty") != "freeStyle"]
    actual_counts = {
        "tracks": len(tracks),
        "lifts": len(lifts),
        "terrainParks": len(terrain_parks),
    }
    if actual_counts != EXPECTED_COUNTS:
        raise ValueError(
            f"Unexpected Devil's Glen status counts: {actual_counts}; "
            f"expected {EXPECTED_COUNTS}"
        )
    return {"lifts": lifts, "tracks": tracks, "terrainParks": terrain_parks}


def main():
    payload = {
        **get_status(),
        "resortId": RESORT_ID,
        "sourceUrl": PAGE_URL,
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
