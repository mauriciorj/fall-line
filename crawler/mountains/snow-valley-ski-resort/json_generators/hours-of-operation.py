"""Snow Valley hours crawler."""

import json
import os
import sys
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dtos import to_hours

URL = "https://www.skisnowvalley.com/about/"
RESORT_ID = "snow-valley-ski-resort"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}


def extract_hours(soup):
    result = {}
    for table in soup.find_all("table"):
        heading = table.find_previous(["h2", "h3", "h4"])
        section_name = heading.get_text(" ", strip=True) if heading else "Hours"
        rows = table.find("tbody").find_all("tr") if table.find("tbody") else table.find_all("tr")
        section = result.setdefault(section_name, {})
        for row in rows:
            cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["td", "th"])]
            if len(cells) >= 2 and cells[0].lower() not in {"day", "date"}:
                section[cells[0]] = cells[1]
    return result


def main():
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    payload = {"hours": to_hours(extract_hours(BeautifulSoup(response.content, "html.parser"))), "resortId": RESORT_ID, "sourceUrl": URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
