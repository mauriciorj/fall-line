import json
import os
import time

import requests
from bs4 import BeautifulSoup

URL = "https://brimacombe.ca/at-the-brim/snow-conditions-and-trails/"
RESORT_ID = "brimacombe"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}
TRAIL_DEFINITIONS = (
    ("1", "Park Avenue", "easy"),
    ("2", "Pete’s Elbow", "easy"),
    ("3", "Snow Bowl", "easy"),
    ("4", "Standard", "medium"),
    ("5", "Bambi", "easy"),
    ("6", "Ladies Downhill", "medium"),
    ("7", "Ben’s Bump", "hard"),
    ("8", "Bowl", "hard"),
    ("9", "Tower Run", "hard"),
    ("10", "Timberline", "hard"),
    ("11", "Flyer", "medium"),
    ("12", "Promenade", "easy"),
    ("13", "Cowpath", "easy"),
    ("14", "Kid’s Stuff", "easy"),
    ("15", "Club House Run", "medium"),
    ("16", "West Ridge", "hard"),
    ("17", "Rutherford’s Cut", "hard"),
    ("18", "Richards’ Landing", "hard"),
    ("19", "Challenger", "hard"),
    ("20", "Whistler", "medium"),
    ("21", "Sunny Side", "medium"),
    ("22", "Nice and Easy", "easy"),
    ("23", "Farmer’s Field", "easy"),
)
LIFT_DEFINITIONS = (
    ("A", "Boulevard Chair"),
    ("B", "Main Street Chair"),
    ("C", "Magic Carpet"),
    ("D", "Bowl Chair"),
    ("E", "T-Bar 5"),
    ("F", "West Chair"),
    ("G", "T-Bar 8"),
)


def normalize_difficulty(value):
    return " ".join(value.lower().split())


def normalize_inventory(lifts, tracks):
    lift_statuses = {(item.get("area"), item.get("name")): item.get("status", "closed") for item in lifts}
    track_statuses = {(item.get("area"), item.get("name")): item for item in tracks}
    return {
        "lifts": [
            {"area": area, "name": name, "status": lift_statuses.get((area, name), "closed")}
            for area, name in LIFT_DEFINITIONS
        ],
        "tracks": [
            {
                "area": area,
                "difficulty": track_statuses.get((area, name), {}).get("difficulty", difficulty),
                "name": name,
                "status": track_statuses.get((area, name), {}).get("status", "closed"),
            }
            for area, name, difficulty in TRAIL_DEFINITIONS
        ],
    }


def parse_trails(table):
    tracks = []
    for row in table.find_all("tr")[1:]:
        cells = row.find_all("td")
        if not cells or len(cells) < 5:
            continue
        image = cells[2].find("img")
        difficulty = normalize_difficulty(image.get("alt", "")) if image else None
        tracks.append(
            {
                "area": cells[0].get_text(strip=True),
                "difficulty": difficulty,
                "name": cells[1].get_text(strip=True),
                "status": cells[3].get_text(strip=True),
            }
        )
    return tracks


def parse_parks(table):
    tracks = []
    for row in table.find_all("tr")[1:]:
        cells = row.find_all("td")
        if not cells or len(cells) < 5:
            continue
        image = cells[2].find("img")
        difficulty = normalize_difficulty(image.get("alt", "")) if image else None
        tracks.append(
            {
                "area": cells[0].get_text(strip=True),
                "difficulty": difficulty,
                "name": cells[1].get_text(strip=True),
                "status": cells[3].get_text(strip=True),
            }
        )
    return tracks


def parse_lifts(table):
    lifts = []
    for row in table.find_all("tr")[1:]:
        cells = row.find_all("td")
        if not cells or len(cells) < 4:
            continue
        lifts.append(
            {
                "area": cells[0].get_text(strip=True),
                "name": cells[1].get_text(strip=True),
                "status": cells[2].get_text(strip=True),
            }
        )
    return lifts


def get_status():
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    tables = BeautifulSoup(response.content, "html.parser").find_all("table")
    tracks = []
    lifts = []
    if len(tables) >= 1:
        tracks.extend(parse_trails(tables[0]))
    if len(tables) >= 2:
        tracks.extend(parse_parks(tables[1]))
    if len(tables) >= 3:
        lifts.extend(parse_lifts(tables[2]))
    return normalize_inventory(lifts, tracks)


def main():
    payload = {
        **get_status(),
        "resortId": RESORT_ID,
        "sourceUrl": URL,
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
