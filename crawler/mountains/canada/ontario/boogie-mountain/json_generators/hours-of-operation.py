import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

RESORT_ID = "boogie-mountain"
SOURCE_URL = "https://boogiemountain.com/location-hours/"
DAYS = (
    "sunday",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
)
HEADERS = {"User-Agent": "Mozilla/5.0"}


def normalize_text(value):
    return " ".join(value.replace("\xa0", " ").split()).lower()


def normalize_time(value):
    value = normalize_text(value)
    return re.sub(r"\s*[-–—�]\s*", " to ", value)


def get_hours():
    response = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
    text = normalize_text(BeautifulSoup(response.content, "html.parser").get_text(" ", strip=True))
    section = re.search(r"opening hours winter:\s*(.*?)(?=\(additional|check for updates)", text, re.IGNORECASE)
    if not section:
        raise ValueError("Could not find Opening Hours Winter section")

    hours = {day: "closed" for day in DAYS}
    day_pattern = r"\b(sunday|monday|tuesday|wednesday|thursday|friday|saturday)\s*:\s*([0-9]{1,2}:?[0-9]{0,2}\s*(?:am|pm)?\s*[-–—�]\s*[0-9]{1,2}:?[0-9]{0,2}\s*(?:am|pm)?)"
    for match in re.finditer(day_pattern, section.group(1), re.IGNORECASE):
        hours[match.group(1).lower()] = normalize_time(match.group(2))
    if all(value == "closed" for value in hours.values()):
        raise ValueError("Could not find weekday hours in Opening Hours Winter section")
    return hours


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
