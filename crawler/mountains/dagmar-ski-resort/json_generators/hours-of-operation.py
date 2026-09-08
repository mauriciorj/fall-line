"""Dagmar hours crawler."""

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

URL = "https://www.skidagmar.com/alpine-rates/"
RESORT_ID = "dagmar-ski-resort"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}


def extract_hours(soup):
    heading = soup.find(string=re.compile(r"Hours of Operation", re.IGNORECASE))
    if not heading:
        return {}
    container = heading.find_parent()
    for _ in range(5):
        if not container:
            return {}
        container = container.find_parent()
        if "Monday" in container.get_text() and "Sunday" in container.get_text():
            break
    result = {}
    for paragraph in container.find_all("p"):
        lines = [line.strip() for line in paragraph.get_text(separator="\n", strip=True).split("\n") if line.strip()]
        if any("Monday" in line for line in lines):
            for line in lines:
                if " - " in line:
                    day, value = line.split(" - ", 1)
                    result[day.strip()] = value.strip()
            break
    return result


def get_hours():
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return extract_hours(BeautifulSoup(response.content, "html.parser"))


def main():
    payload = {"hours": to_hours(get_hours()), "resortId": RESORT_ID, "sourceUrl": URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
