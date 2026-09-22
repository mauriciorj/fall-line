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


def get_lift_rates():
    response = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    table = next(
        (
            table
            for table in soup.find_all("table")
            if "all day - weekdays" in normalize_text(table.get_text(" ", strip=True))
        ),
        None,
    )
    if not table:
        raise ValueError("Could not find All Day - Weekdays lift-ticket row")

    rows = table.find_all("tr")
    headers = [normalize_text(cell.get_text(" ", strip=True)) for cell in rows[0].find_all(["th", "td"])]
    regular_index = next((index for index, header in enumerate(headers) if "regular" in header and "13" in header), None)
    junior_index = next((index for index, header in enumerate(headers) if "junior" in header and "senior" in header), None)
    if regular_index is None or junior_index is None:
        raise ValueError("Could not find regular/junior lift-ticket columns")

    target_row = next(
        (
            row for row in rows[1:]
            if normalize_text(row.find(["td", "th"]).get_text(" ", strip=True)) == "all day - weekdays"
        ),
        None,
    )
    if not target_row:
        raise ValueError("Could not find All Day - Weekdays row")
    cells = target_row.find_all(["td", "th"])
    if len(cells) <= max(regular_index, junior_index):
        raise ValueError("All Day - Weekdays row has insufficient columns")
    adults = parse_price(cells[regular_index].get_text(" ", strip=True))
    youth = parse_price(cells[junior_index].get_text(" ", strip=True))
    if adults is None or youth is None:
        raise ValueError("Missing All Day - Weekdays prices")
    rates = {"adults": adults, "youth": youth, "seniors": youth}
    return {"day-week": dict(rates), "day-weekend": dict(rates)}


def main():
    payload = {"rates": get_lift_rates(), "resortId": RESORT_ID, "sourceUrl": SOURCE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "lift-rates.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
