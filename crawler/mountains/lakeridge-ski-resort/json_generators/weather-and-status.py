"""Lake Ridge trail-status crawler."""

import json
import os
import sys
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dtos import to_weather_dto

URL = "https://ski-lakeridge.com/skiing-snowboarding/trail-status/"
RESORT_ID = "lakeridge-ski-resort"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
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


def get_trail_status():
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table")
    if not table:
        return []
    trails = []
    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 3:
            continue
        trails.append(
            {
                "difficulty": parse_difficulty(cells[0]),
                "name": cells[1].get_text(" ", strip=True),
                "status": cells[2].get_text(" ", strip=True),
            }
        )
    return trails


def main():
    payload = {
        **to_weather_dto(get_trail_status()),
        "resortId": RESORT_ID,
        "sourceUrl": URL,
        "updatedAt": int(time.time() * 1000),
    }
    output_file = os.path.join(os.path.dirname(__file__), "weather-and-status.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
