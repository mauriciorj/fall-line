import json
import os
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

RESORT_ID = "boler-mountain"
SOURCE_URL = "https://www.bolermountain.com/trailmap-2/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}
DIFFICULTIES = {
    "apple jack": "green", "big dip": "black", "dedication": "black", "double dip": "blue",
    "easy street": "green", "elbow": "green", "hill 55": "black", "js": "black",
    "kennedy kruzer": "blue", "red's run": "blue", "rub-a-dub": "blue",
    "rusty's run": "black", "spriet street": "blue", "terrain park": "freeStyle",
    "wayne's way": "black", "willy's bowl": "green",
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


def find_table(soup, title):
    return next(
        (
            table for table in soup.find_all("table")
            if title in normalize_text(table.get_text(" ", strip=True))
        ),
        None,
    )


def parse_tracks(table):
    tracks = []
    for row in table.find_all("tr")[1:]:
        cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["td", "th"])]
        if len(cells) < 2:
            continue
        name = next((value for value in cells if value and normalize_text(value) != "closed" and normalize_text(value) != "open"), "")
        normalized_name = normalize_text(name)
        if not name or normalized_name == "mountain bike trail":
            continue
        status = normalize_status(cells[-1])
        difficulty = DIFFICULTIES.get(normalized_name)
        item = {"name": name, "status": status}
        if difficulty == "freeStyle":
            item["difficulty"] = difficulty
            tracks.append({"terrainPark": item})
        else:
            item["difficulty"] = difficulty
            tracks.append(item)
    return tracks


def parse_lifts(table):
    lifts = []
    for row in table.find_all("tr")[1:]:
        cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["td", "th"])]
        if len(cells) < 2:
            continue
        name = cells[0]
        status = normalize_status(cells[-1])
        if name:
            lifts.append({"name": name, "status": status})
    return lifts


def get_status():
    response = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    trails_table = find_table(soup, "ski & snowboard trails")
    lifts_table = find_table(soup, "ski lifts")
    if not trails_table or not lifts_table:
        raise ValueError("Could not find Boler Ski & Snowboard Trails/Ski Lifts tables")
    parsed = parse_tracks(trails_table)
    tracks = [item for item in parsed if "terrainPark" not in item]
    terrain_parks = [item["terrainPark"] for item in parsed if "terrainPark" in item]
    return {"lifts": parse_lifts(lifts_table), "tracks": tracks, "terrainParks": terrain_parks}


def main():
    payload = {**get_status(), "resortId": RESORT_ID, "sourceUrl": SOURCE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "tracks-and-lifts-weather-status.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
