import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

URL = "https://ski-lakeridge.com/skiing-snowboarding/trail-status/"
RESORT_ID = "lakeridge-ski-resort"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}
DIFFICULTY_FIELDS = {
    "black diamond": "black",
    "double black diamond": "doubleBlack",
    "blue square": "blue",
    "green circle": "green",
    "orange oval": "freeStyle",
}


def parse_difficulty(cell):
    svg = cell.find("svg")
    if not svg:
        return ""
    paths = svg.find_all("path")
    if len(paths) == 2:
        return "Double Black Diamond"
    if svg.find("circle"):
        return "Green Circle"
    rect = svg.find("rect")
    if rect:
        if "rx" in rect.attrs:
            return "Orange Oval"
        if rect.get("fill") == "#4895F7":
            return "Blue Square"
        if rect.get("fill") == "black":
            return "Black Diamond"
    return ""


def normalize_difficulty(value):
    return DIFFICULTY_FIELDS.get(" ".join(value.lower().split()))


def get_trail_status():
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table")
    if not table:
        return []
    tracks = []
    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 3:
            continue
        tracks.append(
            {
                "difficulty": normalize_difficulty(parse_difficulty(cells[0])) or "green",
                "name": cells[1].get_text(" ", strip=True),
                "status": cells[2].get_text(" ", strip=True),
            }
        )
    return tracks


def main():
    payload = {
        "tracks": get_trail_status(),
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
