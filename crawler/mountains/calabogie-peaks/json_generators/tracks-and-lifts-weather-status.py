import json
import os
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

RESORT_ID = "calabogie-peaks"
SOURCE_URL = "https://calabogie.com/trail-status/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}
GRID_DIFFICULTIES = {
    "trail-grid-easy": "green",
    "trail-grid-intermediate": "blue",
    "trail-grid-advanced": "black",
    "trail-grid-parks": "freeStyle",
    "trail-grid-glades": "black",
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


def parse_grid(grid, difficulty):
    values = [value.strip() for value in grid.stripped_strings]
    items = []
    for index in range(3, len(values), 3):
        if index + 1 >= len(values):
            continue
        name = values[index]
        status = normalize_status(values[index + 1])
        if not name or name == "Mountain Bike Trail":
            continue
        items.append({"name": name, "status": status, "difficulty": difficulty})
    return items


def get_status():
    response = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    tracks = []
    terrain_parks = []
    for selector, difficulty in GRID_DIFFICULTIES.items():
        grid = soup.select_one(f".{selector}")
        if not grid:
            continue
        items = parse_grid(grid, difficulty)
        if difficulty == "freeStyle":
            terrain_parks.extend(items)
        else:
            tracks.extend(items)
    lifts = []
    lift_grid = soup.select_one("[class*='lift-grid']")
    if lift_grid:
        values = [value.strip() for value in lift_grid.stripped_strings]
        for index in range(3, len(values), 2):
            if index + 1 < len(values):
                lifts.append({"name": values[index], "status": normalize_status(values[index + 1])})
    if not tracks and not terrain_parks:
        raise ValueError("Could not find Calabogie trail status grids")
    return {"lifts": lifts, "tracks": tracks, "terrainParks": terrain_parks}


def main():
    payload = {**get_status(), "resortId": RESORT_ID, "sourceUrl": SOURCE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "tracks-and-lifts-weather-status.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
