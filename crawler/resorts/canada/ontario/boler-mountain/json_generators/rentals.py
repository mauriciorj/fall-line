import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

RESORT_ID = "boler-mountain"
SOURCE_URL = "https://www.bolermountain.com/day-tickets/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


def normalize_text(value):
    return " ".join(value.lower().split())


def parse_price(value):
    match = re.search(r"\$\s*([0-9]+(?:[.,][0-9]+)?)", value)
    if not match:
        return None
    amount = float(match.group(1).replace(",", "."))
    return f"${int(amount) if amount.is_integer() else amount:g}"


def get_rentals():
    response = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    table = next(
        (
            table
            for table in soup.find_all("table")
            if "equipment rental rates" in normalize_text(table.get_text(" ", strip=True))
            and "ski or snowboard package" in normalize_text(table.get_text(" ", strip=True))
        ),
        None,
    )
    if not table:
        raise ValueError("Could not find Equipment Rental Rates table")

    target_row = next(
        (
            row for row in table.find_all("tr")
            if normalize_text(row.find(["td", "th"]).get_text(" ", strip=True)) == "all day"
        ),
        None,
    )
    if not target_row:
        raise ValueError("Could not find All Day rental row")
    price = parse_price(target_row.get_text(" ", strip=True))
    if price is None:
        raise ValueError("Could not find All Day rental price")
    return {
        "ski": {"adults": price, "youth": price},
        "snowboard": {"adults": price, "youth": price},
        "items": {},
    }


def main():
    payload = {"rentals": get_rentals(), "resortId": RESORT_ID, "sourceUrl": SOURCE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
