import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.mountdufour.com/"
PAGE_URL = "https://www.mountdufour.com/index.php/the-mountain/hours-of-operation"
RESORT_ID = "mount-dufour"
DAYS = ("sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday")
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


def normalize_text(value):
    return " ".join(value.replace("\xa0", " ").split()).lower()


def normalize_time(value):
    value = normalize_text(value)
    if "closed" in value:
        return "closed"
    value = re.sub(r"\s*[-–—]\s*", " to ", value)
    return re.sub(r"\s+(am|pm)\b", r"\1", value)


def get_hours():
    response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    text = normalize_text(BeautifulSoup(response.content, "html.parser").get_text(" ", strip=True))
    start = text.find("hours of operation")
    if start == -1:
        raise ValueError("Could not find Hours of Operation section")
    section = text[start:]
    hours = {}
    for day in DAYS:
        match = re.search(rf"\b{day}\s+(.+?)(?=\s+(?:{'|'.join(DAYS)})\s+|\s+ski hill|$)", section)
        if match:
            hours[day] = normalize_time(match.group(1))
    missing = set(DAYS) - hours.keys()
    if missing:
        raise ValueError(f"Missing Mount Dufour hours: {sorted(missing)}")
    return {day: hours[day] for day in DAYS}


def main():
    payload = {"hours": get_hours(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
