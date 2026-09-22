import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://skihiddenvalley.ca/"
PAGE_URL = "https://skihiddenvalley.ca/explore/hours-of-operation/"
RESORT_ID = "hidden-valley-highlands"
DAYS = ("sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday")
DAY_NAMES = "|".join(day.capitalize() for day in DAYS)
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


def normalize_text(value):
    return " ".join(value.lower().split())


def normalize_time(value):
    value = normalize_text(value)
    if "closed" in value:
        return "closed"
    return re.sub(r"\s*[-–]\s*", " to ", value)


def get_hours():
    response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    text = normalize_text(soup.get_text(" ", strip=True))
    start_marker = "regular season hours monday, january 5, 2026 to saturday, march 14, 2026"
    start = text.find(start_marker)
    if start == -1:
        raise ValueError("Could not find Regular Season Hours section")
    section = text[start + len(start_marker):]
    section = section.split("family day weekend hours", 1)[0]
    hours = {}
    for match in re.finditer(rf"\b({DAY_NAMES})\s+(.+?)(?=\s+(?:{DAY_NAMES})\s+|$)", section, re.IGNORECASE):
        day = match.group(1).lower()
        hours[day] = normalize_time(match.group(2))
    missing = set(DAYS) - hours.keys()
    if missing:
        raise ValueError(f"Missing Regular Season Hours weekdays: {sorted(missing)}")
    return {day: hours[day] for day in DAYS}


def main():
    payload = {"hours": get_hours(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
