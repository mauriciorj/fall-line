import requests
from bs4 import BeautifulSoup
import json
import re
import os

URL = "https://www.skidagmar.com/trailmap/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

DIFFICULTY_MAP = {
    "easy.jpg": "Easy",
    "difficult.jpg": "Difficult",
    "moretdifficult.jpg": "More Difficult",
    "mostdifficult.jpg": "Most Difficult",
    "terrainpark.jpg": "Terrain Park",
}


def parse_lifts(table):
    """Parse the lifts table into a list of dicts."""
    lifts = []
    for tr in table.find_all("tr")[1:]:  # skip header
        cells = tr.find_all("td")
        if not cells or len(cells) < 4:
            continue
        lifts.append({
            "letter": cells[0].get_text(strip=True),
            "name": cells[1].get_text(strip=True),
            "status": cells[3].get_text(strip=True),
        })
    return lifts


def parse_runs(table):
    """Parse the runs table into a list of dicts with difficulty from image src."""
    runs = []
    for tr in table.find_all("tr")[1:]:  # skip header
        cells = tr.find_all("td")
        if not cells or len(cells) < 4:
            continue
        img = cells[0].find("img")
        img_filename = img["src"].split("/")[-1] if img and img.get("src") else ""
        difficulty = DIFFICULTY_MAP.get(img_filename, "")
        runs.append({
            "difficulty": difficulty,
            "name": cells[1].get_text(strip=True),
            "status": cells[3].get_text(strip=True),
        })
    return runs


def parse_daily_conditions(soup):
    """Extract daily conditions (snow base, new snow, conditions)."""
    conditions = {}
    el = soup.find(string=re.compile(r"DAILY CONDITIONS", re.I))
    if not el:
        return conditions

    container = el.find_parent()
    for _ in range(3):
        container = container.find_parent()
        if "Snow Base" in container.get_text():
            break

    for p in container.find_all("p"):
        text = p.get_text(strip=True)
        if ":" in text and "DAILY CONDITIONS" not in text:
            key, value = text.split(":", 1)
            conditions[key.strip()] = value.strip()
    return conditions


def get_trail_status():
    """Fetch and parse trail and lift conditions from Ski Dagmar."""
    print(f"Fetching {URL}...")
    response = requests.get(URL, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    tables = [t for t in soup.find_all("table") if "dz-preview" not in t.get("class", [])]

    result = {}

    if len(tables) >= 1:
        result["Lifts"] = parse_lifts(tables[0])
    if len(tables) >= 2:
        result["Runs"] = parse_runs(tables[1])

    result["Daily Conditions"] = parse_daily_conditions(soup)

    return result


def main():
    status = get_trail_status()
    output_file = os.path.join(os.path.dirname(__file__), "weather-and-status.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
