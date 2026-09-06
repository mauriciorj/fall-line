import json
import os

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

URL = "https://ski-lakeridge.com/skiing-snowboarding/trail-status/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def parse_difficulty(td):
    """Determine trail difficulty from the SVG icon in the cell."""
    svg = td.find("svg")
    if not svg:
        return ""

    # Double black diamond: two <path> elements
    paths = svg.find_all("path")
    if len(paths) == 2:
        return "Double Black Diamond"

    # Green circle
    if svg.find("circle"):
        return "Green Circle"

    rect = svg.find("rect")
    if rect:
        attrs = rect.attrs
        # Orange oval: rect with rounded corners (rx attribute)
        if "rx" in attrs:
            return "Orange Oval"
        fill = attrs.get("fill", "")
        if fill == "#4895F7":
            return "Blue Square"
        if fill == "black":
            return "Black Diamond"

    return ""


def get_trail_status():
    """Fetch and parse the trail status from Ski Lakeridge."""
    print(f"Fetching {URL}...")
    response = requests.get(URL, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table")
    if not table:
        print("No trail status table found.")
        return []

    trails = []
    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if not cells or len(cells) < 3:
            continue

        difficulty = parse_difficulty(cells[0])
        name = cells[1].get_text(strip=True)
        status = cells[2].get_text(strip=True)

        trails.append({
            "difficulty": difficulty,
            "name": name,
            "status": status,
        })

    return trails


def main():
    trails = get_trail_status()
    output_file = os.path.join(os.path.dirname(__file__), "weather-and-status.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(trails, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
