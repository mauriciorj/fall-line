import json
import os
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

RESORT_ID = "hidden-valley-highlands"
SOURCE_URL = "https://msc.skihvh.com/status/embed.php"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}
TRACK_DIFFICULTIES = {
    "Fifth Avenue": "green",
    "Terrain Park": "black",
    "Back Trail": "blue",
    "The Face": "black",
    "Chalet Chute": "blue",
    "Beginner Hill": "green",
    "Lazy Lady": "green",
    "Wild Cat": "black",
    "Dipsy Doodle": "green",
    "Dutchman Glades": "doubleBlack",
    "Nischans Run": "green",
    "Fun Run": "blue",
    "Member's Dip": "doubleBlack",
    "Flying Dutchman": "blue",
}
LIFT_NAMES = {
    "Algonquin Quad (Green Chair)": "Algonquin Quad (Green Chair)",
    "Iroquois Quad (Red Chair)": "Iroquois Quad (Red Chair)",
    "Bigwin Quad (Blue Chair)": "Bigwin Quad (Blue Chair)",
    "Handle Tow": "Handle Tow",
}


def normalize_text(value):
    return " ".join(value.lower().split())


def normalize_status(value):
    value = normalize_text(value)
    if "open" in value:
        return "open"
    if "closed" in value:
        return "closed"
    return value


def get_table_columns(table, required):
    for row in table.find_all("tr"):
        headers = [normalize_text(cell.get_text(" ", strip=True)) for cell in row.find_all(["th", "td"])]
        if all(name in headers for name in required):
            return row, {name: headers.index(name) for name in required}
    return None, None


def find_status_table(soup, heading_text):
    for container in soup.select("div.col-md-6"):
        heading = container.find("h4")
        if heading and normalize_text(heading.get_text(" ", strip=True)) == heading_text:
            table = container.find("table")
            if table:
                return table
    return None


def parse_rows(table, name_column):
    header, columns = get_table_columns(table, (name_column, "day", "night"))
    if not header:
        return []
    rows = table.find_all("tr")
    header_index = rows.index(header)
    return [(row, row.find_all(["td", "th"]), columns) for row in rows[header_index + 1:]]


def parse_runs(table):
    tracks = []
    for _, cells, columns in parse_rows(table, "run"):
        if len(cells) <= max(columns.values()):
            continue
        name = cells[columns["run"]].get_text(" ", strip=True)
        if not name:
            continue
        difficulty = TRACK_DIFFICULTIES.get(name)
        if difficulty is None:
            raise ValueError(f"Unknown Hidden Valley run: {name}")
        tracks.append({
            "name": name,
            "status": normalize_status(cells[columns["day"]].get_text(" ", strip=True)),
            "difficulty": difficulty,
        })
    if not tracks:
        raise ValueError("No Hidden Valley RUNS rows found")
    return tracks


def parse_lifts(table):
    lifts = []
    for _, cells, columns in parse_rows(table, "name"):
        if len(cells) <= max(columns.values()):
            continue
        source_name = cells[columns["name"]].get_text(" ", strip=True)
        if not source_name:
            continue
        name = LIFT_NAMES.get(source_name)
        if name is None:
            raise ValueError(f"Unknown Hidden Valley lift: {source_name}")
        lifts.append({
            "name": name,
            "status": normalize_status(cells[columns["day"]].get_text(" ", strip=True)),
        })
    if not lifts:
        raise ValueError("No Hidden Valley LIFT rows found")
    return lifts


def get_status():
    response = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    runs_table = find_status_table(soup, "runs")
    lifts_table = find_status_table(soup, "lifts")
    if not runs_table or not lifts_table:
        raise ValueError("Could not find Hidden Valley RUNS/LIFTS tables")
    return {"lifts": parse_lifts(lifts_table), "tracks": parse_runs(runs_table), "terrainParks": []}


def main():
    payload = {**get_status(), "resortId": RESORT_ID, "sourceUrl": SOURCE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "tracks-and-lifts-weather-status.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
