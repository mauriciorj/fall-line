import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

RESORT_ID = "antoine-mountain"
SOURCE_URL = "https://antoinemountain.ca/pages/tickets"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}
AGE_GROUPS = {"adults": "adults", "adult": "adults", "junior": "youth", "youth": "youth", "senior": "seniors"}


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
    for table in soup.find_all("table"):
        headers = [normalize_text(cell.get_text(" ", strip=True)) for cell in table.select("thead th")]
        if not headers or not any("adult" in header for header in headers):
            continue
        full_day_row = next(
            (
                row for row in table.select("tbody tr")
                if normalize_text(row.find("td").get_text(" ", strip=True)).startswith("full day")
            ),
            None,
        )
        if not full_day_row:
            continue
        cells = full_day_row.find_all(["td", "th"])
        rates = {}
        for index, header in enumerate(headers[1:], start=1):
            if index >= len(cells):
                continue
            age_group = next((target for source, target in AGE_GROUPS.items() if source in header), None)
            if not age_group:
                continue
            price = parse_price(cells[index].get_text(" ", strip=True))
            if price:
                rates[age_group] = price
        missing = {"adults", "youth", "seniors"} - rates.keys()
        if missing:
            raise ValueError(f"Missing Full Day ticket values: {sorted(missing)}")
        return {"day-week": dict(rates), "day-weekend": dict(rates)}
    raise ValueError("Could not find DAILY LIFT TICKETS Full Day row")


def main():
    payload = {"rates": get_lift_rates(), "resortId": RESORT_ID, "sourceUrl": SOURCE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "lift-rates.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
