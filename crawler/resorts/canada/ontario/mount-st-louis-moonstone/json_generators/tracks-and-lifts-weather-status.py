import json
import os
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

RESORT_ID = "mount-st-louis-moonstone"
SOURCE_URL = "https://www.mountstlouis.com/status/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}
EXPECTED_COUNTS = {"lifts": 11, "tracks": 36, "terrainParks": 5}
AREA_NAMES = {
    "mount st. louis lifts": "Mount St. Louis Slopes",
    "moonstone lifts": "Moonstone Slopes",
    "mount st. louis slopes": "Mount St. Louis Slopes",
    "moonstone slopes": "Moonstone Slopes",
}
DIFFICULTY_NAMES = {
    "easy": "green",
    "more-difficult": "blue",
    "most-difficult": "black",
    "freestyleterrain": "freeStyle",
}


def normalize_status(value):
    normalized = " ".join(value.lower().split())
    if "open" in normalized:
        return "open"
    if "closed" in normalized:
        return "closed"
    return normalized


def normalize_area(value):
    normalized = " ".join(value.lower().split())
    return AREA_NAMES.get(normalized, value.strip())


def get_difficulty(cell):
    icon = cell.find("i", class_=lambda value: value and "difficulty" in value)
    if not icon:
        return None

    classes = set(icon.get("class", []))
    for source, target in DIFFICULTY_NAMES.items():
        if source in classes:
            return target
    return None


def parse_table(table, include_difficulty=False):
    items = []
    for row in table.select("tr"):
        cells = row.find_all("td")
        if len(cells) < 2:
            continue

        name = cells[0].get_text(" ", strip=True)
        status = cells[1].get_text(" ", strip=True)
        if not name or not status:
            continue

        item = {"name": name, "status": normalize_status(status)}
        if include_difficulty:
            difficulty = get_difficulty(cells[2]) if len(cells) > 2 else None
            if difficulty:
                item["difficulty"] = difficulty
        items.append(item)

    return items


def parse_day_section(soup, section_id, include_difficulty=False):
    section = soup.select_one(f"#{section_id}")
    if not section:
        raise ValueError(f"Missing status section: {section_id}")

    day_panel = section.select_one(
        ".tab-pane[id$='-runs'], .tab-pane[id$='-lifts'], .col-md-6"
    )
    if section_id == "open-parks":
        day_panel = section.select_one(".col-md-6")
    elif section_id == "open-slopes":
        day_panel = section.select_one("#day-runs")
    elif section_id == "open-lifts":
        day_panel = section.select_one("#day-lifts")

    if not day_panel:
        raise ValueError(f"Missing day status panel: {section_id}")

    items = []
    for column in day_panel.select(":scope > .row > .col-md-6"):
        heading = column.find(["h2", "h4"])
        area = normalize_area(heading.get_text(" ", strip=True)) if heading else None
        table = column.find("table")
        if not table:
            continue
        for item in parse_table(table, include_difficulty):
            if area:
                item["area"] = area
            items.append(item)

    if not items:
        table = day_panel.find("table")
        if table:
            items = parse_table(table, include_difficulty)

    return items


def get_status():
    response = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    tracks = parse_day_section(soup, "open-slopes", include_difficulty=True)
    parks = parse_day_section(soup, "open-parks", include_difficulty=False)
    lifts = parse_day_section(soup, "open-lifts", include_difficulty=False)

    for park in parks:
        park["difficulty"] = "freeStyle"

    actual_counts = {
        "lifts": len(lifts),
        "tracks": len(tracks),
        "terrainParks": len(parks),
    }
    if actual_counts != EXPECTED_COUNTS:
        raise ValueError(
            f"Unexpected Mount St. Louis status counts: {actual_counts}; "
            f"expected {EXPECTED_COUNTS}"
        )

    return {"lifts": lifts, "tracks": tracks, "terrainParks": parks}


def main():
    payload = {
        **get_status(),
        "resortId": RESORT_ID,
        "sourceUrl": SOURCE_URL,
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
