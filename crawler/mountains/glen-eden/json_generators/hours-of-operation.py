"""
Glen Eden hours crawler.
Scrapes hours from https://gleneden.on.ca/plan-your-visit/.
"""

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
from dtos import to_hours

URL = "https://gleneden.on.ca/plan-your-visit/"
RESORT_ID = "glen-eden"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def extract_hours(soup):
    text = soup.get_text(" ", strip=True)
    result = {}

    regular_match = re.search(
        r"Regular Hours:\s*(.+?)\s*Holiday Hours:", text, re.IGNORECASE
    )
    if regular_match:
        result["Regular Hours"] = {"Daily": regular_match.group(1).strip()}

    holiday_match = re.search(
        r"Holiday Hours:\s*(.+?)(?:Pass Details|Frequently Asked Questions|$)",
        text,
        re.IGNORECASE,
    )
    if holiday_match:
        result["Holiday Hours"] = {"Holiday periods": holiday_match.group(1).strip()}
    return result


def get_hours():
    print(f"Fetching {URL}...")
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return extract_hours(BeautifulSoup(response.content, "html.parser"))


def main():
    payload = {
        "hours": to_hours(get_hours()),
        "resortId": RESORT_ID,
        "sourceUrl": URL,
        "updatedAt": int(time.time() * 1000),
    }
    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
