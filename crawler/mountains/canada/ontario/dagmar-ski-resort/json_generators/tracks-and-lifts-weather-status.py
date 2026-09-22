import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

URL = "https://www.skidagmar.com/trailmap/"
RESORT_ID = "dagmar-ski-resort"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
}
DIFFICULTY_FIELDS = {
    "easy": "green",
    "difficult": "blue",
    "more difficult": "black",
    "most difficult": "doubleBlack",
    "terrain park": "freeStyle",
}
LIFT_NAMES = (
    ("A", "Big Daddy"),
    ("B", "Little Momma"),
    ("C", "East Magic Carpet"),
    ("D", "Rendez-Vous"),
    ("E", "West Magic Carpet"),
    ("F", "Favourite"),
)
RUN_NAMES = (
    ("1", "Park View"),
    ("2", "Puppy Pound"),
    ("3", "Dog Pound"),
    ("4", "Impound"),
    ("5", "Impound Jumpline"),
    ("6", "Compound Snow Zone"),
    ("7", "Compound"),
    ("8", "The Chute"),
    ("9", "Little Momma"),
    ("10", "Pony"),
    ("11", "Rendez Vous"),
    ("12", "Bomber"),
    ("13", "Upper Lovers Lane"),
    ("14", "Lower Lovers Lane"),
    ("15", "Club House"),
    ("16", "Favourite"),
    ("17", "Alleyway"),
    ("18", "Elbow"),
    ("19", "The Dagger"),
    ("20", "The Glades"),
)
RUN_DIFFICULTIES = {
    "Park View": "green",
    "Puppy Pound": "freeStyle",
    "Dog Pound": "freeStyle",
    "Impound": "freeStyle",
    "Impound Jumpline": "freeStyle",
    "Compound Snow Zone": "freeStyle",
    "Compound": "freeStyle",
    "The Chute": "blue",
    "Little Momma": "green",
    "Pony": "green",
    "Rendez Vous": "blue",
    "Bomber": "black",
    "Upper Lovers Lane": "green",
    "Lower Lovers Lane": "green",
    "Club House": "blue",
    "Favourite": "green",
    "Alleyway": "blue",
    "Elbow": "blue",
    "The Dagger": "doubleBlack",
    "The Glades": "doubleBlack",
}


def normalize_difficulty(value):
    return DIFFICULTY_FIELDS.get(" ".join(value.lower().split()))


def split_run_name(value):
    text = " ".join(value.split())
    match = re.match(r"^([^\s-]+)\s*[-–:]\s*(.+)$", text)
    if match:
        return match.group(1).rstrip("."), match.group(2).strip()
    parts = text.split(None, 1)
    return (parts[0], parts[1]) if len(parts) == 2 else ("", text)


def parse_lifts(table):
    lifts = []
    for row in table.find_all("tr")[1:]:
        cells = row.find_all("td")
        if len(cells) < 4:
            continue
        lifts.append(
            {
                "area": cells[0].get_text(strip=True),
                "name": cells[1].get_text(strip=True),
                "status": cells[3].get_text(strip=True),
            }
        )
    return lifts


def parse_runs(table):
    tracks = []
    for row in table.find_all("tr")[1:]:
        cells = row.find_all("td")
        if len(cells) < 4:
            continue
        image = cells[0].find("img")
        difficulty = normalize_difficulty(image.get("alt", "") if image else "")
        area, name = split_run_name(cells[1].get_text(" ", strip=True))
        tracks.append(
            {
                "area": area,
                "difficulty": difficulty or "green",
                "name": name,
                "status": cells[3].get_text(strip=True),
            }
        )
    return tracks


def normalize_inventory(lifts, tracks):
    lift_statuses = {(item.get("area"), item.get("name")): item.get("status", "closed") for item in lifts}
    track_statuses = {(item.get("area"), item.get("name")): item for item in tracks}
    return {
        "lifts": [
            {
                "area": area,
                "name": name,
                "status": lift_statuses.get((area, name), "closed"),
            }
            for area, name in LIFT_NAMES
        ],
        "tracks": [
            {
                "area": area,
                "difficulty": RUN_DIFFICULTIES.get(
                    name,
                    track_statuses.get((area, name), {}).get("difficulty", "green"),
                ),
                "name": name,
                "status": track_statuses.get((area, name), {}).get("status", "closed"),
            }
            for area, name in RUN_NAMES
        ],
    }


def get_status():
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    tables = [
        table
        for table in soup.find_all("table")
        if "dz-preview" not in table.get("class", [])
    ]
    return normalize_inventory(
        parse_lifts(tables[0]) if len(tables) >= 1 else [],
        parse_runs(tables[1]) if len(tables) >= 2 else [],
    )


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
