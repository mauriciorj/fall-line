import requests
from bs4 import BeautifulSoup
import json
import os

URL = "https://brimacombe.ca/at-the-brim/snow-conditions-and-trails/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def parse_trails(table):
    """Parse trails table: number, name, difficulty (from img alt), day/night status."""
    trails = []
    for tr in table.find_all("tr")[1:]:  # skip header
        cells = tr.find_all("td")
        if not cells or len(cells) < 5:
            continue
        img = cells[2].find("img")
        difficulty = img["alt"].capitalize() if img and img.get("alt") else ""
        trails.append({
            "number": cells[0].get_text(strip=True),
            "name": cells[1].get_text(strip=True),
            "difficulty": difficulty,
            "day": cells[3].get_text(strip=True),
            "night": cells[4].get_text(strip=True),
        })
    return trails


def parse_parks(table):
    """Parse parks table: code, name, difficulty (from img alt), day/night status."""
    parks = []
    for tr in table.find_all("tr")[1:]:
        cells = tr.find_all("td")
        if not cells or len(cells) < 5:
            continue
        img = cells[2].find("img")
        difficulty = img["alt"].capitalize() if img and img.get("alt") else ""
        parks.append({
            "code": cells[0].get_text(strip=True),
            "name": cells[1].get_text(strip=True),
            "difficulty": difficulty,
            "day": cells[3].get_text(strip=True),
            "night": cells[4].get_text(strip=True),
        })
    return parks


def parse_lifts(table):
    """Parse lifts table: letter, name, day/night status."""
    lifts = []
    for tr in table.find_all("tr")[1:]:
        cells = tr.find_all("td")
        if not cells or len(cells) < 4:
            continue
        lifts.append({
            "letter": cells[0].get_text(strip=True),
            "name": cells[1].get_text(strip=True),
            "day": cells[2].get_text(strip=True),
            "night": cells[3].get_text(strip=True),
        })
    return lifts


def get_trail_status():
    """Fetch and parse trail, park, and lift status from Brimacombe."""
    print(f"Fetching {URL}...")
    response = requests.get(URL, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    tables = soup.find_all("table")
    result = {}

    if len(tables) >= 1:
        result["Trails"] = parse_trails(tables[0])
    if len(tables) >= 2:
        result["Parks"] = parse_parks(tables[1])
    if len(tables) >= 3:
        result["Lifts"] = parse_lifts(tables[2])

    return result


def main():
    status = get_trail_status()
    output_file = os.path.join(os.path.dirname(__file__), "weather-and-status.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
