"""Dagmar trail-status crawler."""

import json
import os
import re
import sys
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dtos import to_weather_dto

URL = "https://www.skidagmar.com/trailmap/"
RESORT_ID = "dagmar-ski-resort"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
DIFFICULTY_MAP = {"easy.jpg": "Easy", "difficult.jpg": "Difficult", "moretdifficult.jpg": "More Difficult", "mostdifficult.jpg": "Most Difficult", "terrainpark.jpg": "Terrain Park"}


def parse_lifts(table):
    result = []
    for row in table.find_all("tr")[1:]:
        cells = row.find_all("td")
        if len(cells) >= 4:
            result.append({"letter": cells[0].get_text(strip=True), "name": cells[1].get_text(strip=True), "status": cells[3].get_text(strip=True)})
    return result


def parse_runs(table):
    result = []
    for row in table.find_all("tr")[1:]:
        cells = row.find_all("td")
        if len(cells) < 4:
            continue
        image = cells[0].find("img")
        filename = image.get("src", "").split("/")[-1] if image else ""
        result.append({"difficulty": DIFFICULTY_MAP.get(filename, ""), "name": cells[1].get_text(strip=True), "status": cells[3].get_text(strip=True)})
    return result


def parse_daily_conditions(soup):
    element = soup.find(string=re.compile(r"DAILY CONDITIONS", re.IGNORECASE))
    if not element:
        return {}
    container = element.find_parent()
    for _ in range(3):
        container = container.find_parent()
        if "Snow Base" in container.get_text():
            break
    result = {}
    for paragraph in container.find_all("p"):
        text = paragraph.get_text(strip=True)
        if ":" in text and "DAILY CONDITIONS" not in text:
            key, value = text.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def get_trail_status():
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    tables = [table for table in soup.find_all("table") if "dz-preview" not in table.get("class", [])]
    status = {}
    if len(tables) >= 1:
        status["Lifts"] = parse_lifts(tables[0])
    if len(tables) >= 2:
        status["Runs"] = parse_runs(tables[1])
    status["Daily Conditions"] = parse_daily_conditions(soup)
    return status


def main():
    payload = {**to_weather_dto(get_trail_status()), "resortId": RESORT_ID, "sourceUrl": URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "weather-and-status.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
