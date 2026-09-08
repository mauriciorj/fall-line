"""Horseshoe Valley Resort rental rates crawler."""

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
from dtos import to_rentals_dto

RESORT_ID = "horseshoe-valley-resort"
SOURCE_URL = "https://horseshoeresort.com/ski/lift-ticket-and-rentals-pricing/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def get_rentals():
    response = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    result = {}
    for index, table in enumerate(soup.find_all("table"), 1):
        heading = table.find_previous(["h3", "h4", "h5"])
        heading_text = heading.get_text(" ", strip=True) if heading else ""
        rows = table.find_all("tr")
        if not rows:
            continue
        headers = [cell.get_text(" ", strip=True) for cell in rows[0].find_all(["th", "td"])]
        header_text = " ".join(headers)
        if "rental" not in heading_text.lower() and "rental" not in header_text.lower():
            continue
        section_name = heading_text or f"rental_table_{index}"
        section = result.setdefault(section_name, [])
        for row in rows[1:]:
            cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["td", "th"])]
            if len(cells) < 2 or not cells[0] or not any(re.search(r"\$\d+", cell) for cell in cells):
                continue
            item = {"item": re.sub(r"\*.*$", "", cells[0]).strip()}
            if len(cells) >= 4:
                item.update({"age_group": cells[1], "midweek_price": cells[2], "weekend_price": cells[3]})
            elif len(cells) == 3:
                item.update({"age_group": cells[1], "closing_weekend": cells[2]})
            else:
                item["price"] = cells[1]
            section.append(item)
    return result


def main():
    payload = {
        "rentals": to_rentals_dto(get_rentals()),
        "resortId": RESORT_ID,
        "sourceUrl": SOURCE_URL,
        "updatedAt": int(time.time() * 1000),
    }
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
