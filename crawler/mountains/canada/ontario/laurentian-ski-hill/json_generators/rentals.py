import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

RESORT_ID = "laurentian-ski-hill-north-bay"
SOURCE_URL = "https://laurentianskihill.com/rentals/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}
PRICE_PATTERN = re.compile(r"\$\s*([0-9]+(?:[.,][0-9]+)?)")


def normalize_text(value):
    return " ".join(value.lower().split())


def parse_price(value):
    match = PRICE_PATTERN.search(value)
    if not match:
        return None
    amount = float(match.group(1).replace(",", "."))
    return f"${int(amount) if amount.is_integer() else amount:g}"


def get_rentals():
    response = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    table = next((table for table in soup.find_all("table") if normalize_text(table.get("aria-label", "")) == "equipment rentals"), None)
    if not table:
        table = next((table for table in soup.find_all("table") if "equipment rentals" in normalize_text(table.find_parent().get_text(" ", strip=True))), None)
    if not table:
        raise ValueError("Could not find Equipment Rentals table")

    headers = [normalize_text(cell.get_text(" ", strip=True)) for cell in table.select("thead th")]
    full_day_index = next((index for index, header in enumerate(headers) if header == "full day"), None)
    if full_day_index is None:
        raise ValueError("Could not find Full Day column")

    rentals = {"ski": {}, "snowboard": {}, "items": {}}
    for row in table.select("tbody tr"):
        cells = row.find_all(["th", "td"])
        if len(cells) <= full_day_index:
            continue
        label = normalize_text(cells[0].get_text(" ", strip=True))
        price = parse_price(cells[full_day_index].get_text(" ", strip=True))
        if not price:
            continue
        if label == "complete rental package – adult":
            rentals["ski"]["adults"] = price
            rentals["snowboard"]["adults"] = price
        elif label == "complete rental package – junior (6-12), student & senior (60+)":
            rentals["ski"]["youth"] = price
            rentals["snowboard"]["youth"] = price
        elif label == "snowboard or skis only":
            rentals["items"]["skis"] = price
            rentals["items"]["snowboard"] = price
        elif label == "helmet only":
            rentals["items"]["helmet"] = price
        elif label == "boots only":
            rentals["items"]["boots"] = price
        elif label == "poles only":
            rentals["items"]["poles"] = price
        elif label == "snowshoes":
            rentals["items"]["snowshoes"] = price

    expected = {
        ("ski", "adults"),
        ("ski", "youth"),
        ("snowboard", "adults"),
        ("snowboard", "youth"),
    }
    missing = [f"{category}.{item}" for category, item in expected if item not in rentals[category]]
    missing.extend(item for item in ("skis", "snowboard", "helmet", "boots", "poles", "snowshoes") if item not in rentals["items"])
    if missing:
        raise ValueError(f"Missing Full Day rental prices: {sorted(missing)}")
    return rentals


def main():
    payload = {"rentals": get_rentals(), "resortId": RESORT_ID, "sourceUrl": SOURCE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
