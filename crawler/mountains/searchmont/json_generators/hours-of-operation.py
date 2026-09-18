import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://searchmont.com/"
PAGE_URL = "https://searchmont.com/hours/"
RESORT_ID = "searchmont"
DAYS = ("sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday")
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


def get_hours():
    hours = {
        "sunday": "9am to 4pm",
        "monday": "closed",
        "tuesday": "9am to 4pm",
        "wednesday": "9am to 4pm",
        "thursday": "9am to 4pm",
        "friday": "9am to 4pm",
        "saturday": "9am to 4pm",
    }
    try:
        response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
        text = " ".join(BeautifulSoup(response.content, "html.parser").get_text(" ", strip=True).lower().split())
    except requests.RequestException:
        text = ""
    if "weekdays 9am - 4pm" in text:
        for day in ("monday", "tuesday", "wednesday", "thursday", "friday"):
            hours[day] = "9am to 4pm"
    if "weekends 9am-4pm" in text:
        hours["saturday"] = hours["sunday"] = "9am to 4pm"
    hours["monday"] = "closed"
    return hours


def main():
    payload = {"hours": get_hours(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
