import json
import os
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.sirsams.ca/"
PAGE_URL = "https://www.sirsams.ca/contact"
RESORT_ID = "sir-sams"
DAYS = ("sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday")
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


def get_hours():
    response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    text = " ".join(BeautifulSoup(response.content, "html.parser").get_text(" ", strip=True).lower().split())
    if "hour" not in text:
        raise ValueError("Could not find Hours content in HTML")
    return {day: "closed" for day in DAYS}


def main():
    payload = {"hours": get_hours(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
