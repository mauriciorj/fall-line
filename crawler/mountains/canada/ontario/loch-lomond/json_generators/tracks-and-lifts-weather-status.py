import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.lochlomond.ca/"
PAGE_URL = "https://www.lochlomond.ca/conditions/"
RESORT_ID = "loch-lomond"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}
AREA_TRACKS = {
    "South Chairlift": {
        "Upper Sunbowl": "green",
        "Lower Sunbowl": "green",
        "Cliff": "blue",
        "Mullet": "blue",
        "Upper Pine": "blue",
        "Lower Pine": "blue",
        "Pine Glades": "blue",
    },
    "North Chairlift": {
        "Chicken": "green",
        "Kitzbuel": "green",
        "Upper Maple": "blue",
        "Lower Maple": "blue",
        "Zipper": "blue",
        "Birch": "black",
        "Old Joe's": "black",
        "Giant": "black",
        "Jolly Giant": "doubleBlack",
        "Devil's Dive": "doubleBlack",
        "Devil's Playground": "doubleBlack",
    },
    "Snoopy Chairlift": {
        "Lower Sunbowl": "green",
        "Terrain Park": "freeStyle",
    },
}
LIFTS = tuple(AREA_TRACKS)


def normalize_text(value):
    return " ".join(value.replace("\xa0", " ").split()).lower()


def normalize_name(value):
    value = value.replace("’", "'").lower()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def normalize_status(value):
    return normalize_text(value)


def parse_area_statuses(soup, area, expected_tracks):
    heading = next(
        (
            element
            for element in soup.find_all(["h2", "h3", "h4"])
            if normalize_text(element.get_text(" ", strip=True)) == area.lower()
        ),
        None,
    )
    if not heading:
        raise ValueError(f"Could not find {area} section")
    table = heading.find_next("table")
    if not table:
        raise ValueError(f"Could not find {area} status table")

    header = next(
        (
            row
            for row in table.find_all("tr")
            if "status" in [normalize_text(cell.get_text(" ", strip=True)) for cell in row.find_all(["th", "td"])]
        ),
        None,
    )
    if not header:
        raise ValueError(f"Could not find {area} status columns")
    headers = [normalize_text(cell.get_text(" ", strip=True)) for cell in header.find_all(["th", "td"])]
    status_index = headers.index("status")
    name_index = 0
    statuses = {}
    for row in table.find_all("tr"):
        cells = row.find_all(["th", "td"])
        if len(cells) <= status_index or row is header:
            continue
        name = normalize_name(cells[name_index].get_text(" ", strip=True))
        expected_name = next((track for track in expected_tracks if normalize_name(track) == name), None)
        if expected_name:
            statuses[expected_name] = normalize_status(cells[status_index].get_text(" ", strip=True))

    missing = set(expected_tracks) - statuses.keys()
    if missing:
        raise ValueError(f"Missing {area} status rows: {sorted(missing)}")
    return statuses


def get_status():
    response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    statuses = {area: parse_area_statuses(soup, area, tracks) for area, tracks in AREA_TRACKS.items()}
    tracks = []
    terrain_parks = []
    for area, area_tracks in AREA_TRACKS.items():
        for name, difficulty in area_tracks.items():
            tracks.append({"name": name, "status": statuses[area][name], "difficulty": difficulty})
    return {
        "lifts": [{"name": name, "status": "closed"} for name in LIFTS],
        "tracks": tracks,
        "terrainParks": terrain_parks,
    }


def main():
    payload = {**get_status(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "tracks-and-lifts-weather-status.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
