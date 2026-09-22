import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

RESORT_ID = "adanac-ski-hill"
SOURCE_URL = "https://www.greatersudbury.ca/play/ski-hills/adanac-ski-hill/fees-and-rentals/lift-tickets/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}
AGE_GROUPS = {"junior": "youth", "youth": "youth", "adult": "adults", "senior": "seniors"}


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
            if "full day price" in normalize_text(table.get_text(" ", strip=True))
        ),
        None,
    )
    if not table:
        raise ValueError("Could not find Lift Ticket Prices table")

    rows = table.find_all("tr")
    headers = [normalize_text(cell.get_text(" ", strip=True)) for cell in rows[0].find_all(["th", "td"])]
    full_day_index = next((index for index, header in enumerate(headers) if "full day price" in header), None)
    if full_day_index is None:
        raise ValueError("Could not find Full Day Price column")

    rates = {}
    for row in rows[1:]:
        cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["th", "td"])]
        if len(cells) <= full_day_index:
            continue
        label = normalize_text(cells[0])
        age_group = next((target for source, target in AGE_GROUPS.items() if source in label), None)
        if not age_group:
            continue
        price = parse_price(cells[full_day_index])
        if price:
            rates[age_group] = price

    missing = {"adults", "youth", "seniors"} - rates.keys()
    if missing:
        raise ValueError(f"Missing Full Day Price values: {sorted(missing)}")
    return {"day-week": dict(rates), "day-weekend": dict(rates)}


def main():
    payload = {"rates": get_lift_rates(), "resortId": RESORT_ID, "sourceUrl": SOURCE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "lift-rates.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
