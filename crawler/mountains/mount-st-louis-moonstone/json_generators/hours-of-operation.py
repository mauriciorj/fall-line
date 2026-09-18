import json
import os
import time
from datetime import date

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

RESORT_ID = "mount-st-louis-moonstone"
SOURCE_URL = "https://shop.mountstlouis.com/"
DAYS = (
    "sunday",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}


def fetch_soup():
    response = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser")


def normalize_text(value):
    return " ".join(value.lower().split())


def normalize_hours(value):
    normalized = normalize_text(value)
    return "closed" if "closed" in normalized else normalized


def get_hours():
    table = fetch_soup().select_one("table.hours")
    if not table:
        raise ValueError("Could not find hours table")

    today = DAYS[(date.today().weekday() + 1) % 7]
    hours = {}
    rows = table.select("tbody tr") or table.find_all("tr")
    for row in rows:
        heading = row.find("th", scope="row") or row.find("th")
        value = row.find("td")
        if not heading or not value:
            continue

        day = normalize_text(heading.get_text(" ", strip=True))
        day = today if day == "today" else day
        if day in DAYS:
            hours[day] = normalize_hours(value.get_text(" ", strip=True))

    missing_days = [day for day in DAYS if day not in hours]
    if missing_days:
        raise ValueError(f"Missing hours for: {missing_days}")
    return {day: hours[day] for day in DAYS}


def main():
    payload = {
        "hours": get_hours(),
        "resortId": RESORT_ID,
        "sourceUrl": SOURCE_URL,
        "updatedAt": int(time.time() * 1000),
    }
    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()