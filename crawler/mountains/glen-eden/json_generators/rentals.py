"""
Glen Eden rental rates crawler.
Scrapes rental rates from https://gleneden.on.ca/plan-your-visit/.
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
from dtos import to_rentals_dto

RESORT_ID = "glen-eden"
SOURCE_URL = "https://gleneden.on.ca/plan-your-visit/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def is_price(text):
    return bool(re.search(r"\$\d+", text))


def fetch_page(url):
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.text


def parse_rentals(html):
    result = {
        "rental_daily_packages": [],
        "rental_single_items": [],
        "rental_lesson_packages": [],
    }
    soup = BeautifulSoup(html, "html.parser")
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if not rows:
            continue
        headers = [cell.get_text(" ", strip=True).lower() for cell in rows[0].find_all(["th", "td"])]
        header_text = " ".join(headers)
        is_lift_ticket_table = (
            ("peak" in header_text and "off" in header_text)
            or (
                "age" in header_text
                and any(is_price(cell.get_text()) for row in rows[1:] for cell in row.find_all(["td", "th"]))
            )
        )
        if "rate" not in header_text or is_lift_ticket_table:
            continue
        for row in rows[1:]:
            cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["td", "th"])]
            if len(cells) < 2 or not cells[0] or not any(is_price(cell) for cell in cells):
                continue
            item_name = cells[0]
            price = next((cell for cell in cells[1:] if is_price(cell)), None)
            if "lesson" in item_name.lower():
                section = "rental_lesson_packages"
            elif any(word in item_name.lower() for word in ["helmet", "poles", "boots", "skis", "snowboard"]):
                section = "rental_single_items"
            else:
                section = "rental_daily_packages"
            result[section].append({"item": item_name, "price": price})
    return result


def get_rentals(url=SOURCE_URL):
    return parse_rentals(fetch_page(url))


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
