import json
import os
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

RESORT_ID = "laurentian-ski-hill-north-bay"
SOURCE_URL = "https://laurentianskihill.com/plan-a-visit/trail-map/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}
TRACK_DIFFICULTIES = {
    "Beginner Hill": "green",
    "No Name": "green",
    "Ron's Run": "green",
    "Slingshot": "blue",
    "Poutine Pitch": "blue",
    "Maples": "blue",
    "Steve Omischl": "black",
    "Aeroplane": "black",
    "Upper Jack's Back": "freeStyle",
    "Terrain Park": "freeStyle",
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


def get_status():
    response = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    heading = next((element for element in soup.find_all(["h1", "h2", "h3", "h4"]) if normalize_text(element.get_text(" ", strip=True)) == "live trail status"), None)
    if not heading:
        raise ValueError("Could not find Live Trail Status section")

    container = heading.find_parent(class_=lambda value: value and "fl-col-content" in value)
    status_wrapper = container.select_one(".status-wrapper") if container else None
    if not status_wrapper:
        raise ValueError("Could not find Live Trail Status values")

    tracks = []
    terrain_parks = []
    for row in status_wrapper.select(".status-row"):
        title = row.select_one(".status-title")
        status = row.select_one(".status-status")
        if not title or not status:
            continue
        name = title.get_text(" ", strip=True)
        difficulty = TRACK_DIFFICULTIES.get(name)
        if difficulty is None:
            raise ValueError(f"Unknown Laurentian trail: {name}")
        item = {"name": name, "status": normalize_status(status.get_text(" ", strip=True)), "difficulty": difficulty}
        (terrain_parks if difficulty == "freeStyle" else tracks).append(item)

    if len(tracks) + len(terrain_parks) != len(TRACK_DIFFICULTIES):
        raise ValueError("Missing Laurentian Live Trail Status rows")
    return {"lifts": [], "tracks": tracks, "terrainParks": terrain_parks}


def main():
    payload = {**get_status(), "resortId": RESORT_ID, "sourceUrl": SOURCE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "tracks-and-lifts-weather-status.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
