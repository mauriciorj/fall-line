"""Horseshoe Valley Resort lift-ticket rates crawler."""

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
from dtos import to_rates_dto

RESORT_ID = "horseshoe-valley-resort"
SOURCE_URL = "https://horseshoeresort.com/ski/lift-ticket-and-rentals-pricing/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def get_lift_rates():
    response = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    data = {"lift_tickets": []}
    for table in soup.find_all("table"):
        heading = table.find_previous(["h3", "h4", "h5"])
        heading_text = heading.get_text(" ", strip=True) if heading else ""
        rows = table.find_all("tr")
        if not rows:
            continue
        headers = [cell.get_text(" ", strip=True) for cell in rows[0].find_all(["th", "td"])]
        if "rental" in heading_text.lower() or "rental" in " ".join(headers).lower():
            continue
        for row in rows[1:]:
            cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["td", "th"])]
            if len(cells) < 2 or not cells[0] or not any(re.search(r"\$\d+", cell) for cell in cells):
                continue
            item = {
                "category": cells[0],
                "age_group": cells[1] if len(cells) > 2 else "",
            }
            if len(cells) == 2:
                item["closing_weekend"] = cells[1]
            elif len(cells) >= 3:
                item["midweek_price"] = cells[1]
                item["weekend_price"] = cells[2]
            data["lift_tickets"].append(item)
    return data


def main():
    payload = {
        "rates": to_rates_dto(get_lift_rates()),
        "resortId": RESORT_ID,
        "sourceUrl": SOURCE_URL,
        "updatedAt": int(time.time() * 1000),
    }
    output_file = os.path.join(os.path.dirname(__file__), "lift-rates.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
