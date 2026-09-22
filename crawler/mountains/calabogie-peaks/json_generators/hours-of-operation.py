import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://calabogie.com/"
PAGE_URL = SOURCE_URL
RESORT_ID = "calabogie-peaks"
DAYS = ("sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday")
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


def normalize_text(value):
    return " ".join(value.lower().split())


def get_hours():
    response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    footer = soup.find("footer")
    text = normalize_text((footer or soup).get_text(" ", strip=True))
    match = re.search(
        r"hours of operation.*?lift\s*:\s*([0-9]{1,2}:?[0-9]{0,2}\s*(?:am|pm)\s*[-–]\s*[0-9]{1,2}:?[0-9]{0,2}\s*(?:am|pm))",
        text,
        re.IGNORECASE,
    )
    if not match:
        raise ValueError("Could not find footer Hours of Operation Lift value")
    lift_hours = re.sub(r"\s*[-–]\s*", " to ", normalize_text(match.group(1)))
    return {day: lift_hours for day in DAYS}


def main():
    payload = {"hours": get_hours(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
