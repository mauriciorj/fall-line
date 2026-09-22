import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.bolermountain.com/"
PAGE_URL = "https://www.bolermountain.com/hours-of-operation/"
RESORT_ID = "boler-mountain"
DAYS = ("sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday")
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


def normalize_text(value):
    return " ".join(value.lower().split())


def get_weekday(value):
    normalized = normalize_text(value)
    return next((day for day in DAYS if re.search(rf"\b{day}\b", normalized)), None)


def normalize_time(value):
    normalized = normalize_text(value)
    if "closed" in normalized:
        return "closed"
    return re.sub(r"\s*[-–]\s*", " to ", normalized)


def get_hours():
    response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    heading = next((element for element in soup.find_all(["h1", "h2", "h3", "h4"]) if "ski/snowboard hours of operation" in normalize_text(element.get_text(" ", strip=True))), None)
    if not heading:
        raise ValueError("Could not find Ski/Snowboard Hours of Operation section")
    table = heading.find_next("table")
    if not table:
        raise ValueError("Could not find Ski/Snowboard Hours of Operation table")

    hours = {}
    for row in table.find_all("tr"):
        cells = row.find_all(["th", "td"])
        if len(cells) < 2:
            continue
        day = get_weekday(cells[0].get_text(" ", strip=True))
        if day:
            hours[day] = normalize_time(cells[1].get_text(" ", strip=True))

    missing = set(DAYS) - hours.keys()
    if missing:
        raise ValueError(f"Missing weekday hours: {sorted(missing)}")
    return {day: hours[day] for day in DAYS}


def main():
    payload = {"hours": get_hours(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
