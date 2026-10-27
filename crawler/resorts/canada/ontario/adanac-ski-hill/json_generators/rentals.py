import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

RESORT_ID = "adanac-ski-hill"
SOURCE_URL = "https://www.greatersudbury.ca/play/ski-hills/adanac-ski-hill/fees-and-rentals/equipment-rentals"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}
PACKAGE_NAME = "snowboard & boots or skis, boots & poles & helmet"
REQUIRED_ITEMS = {"skis", "snowboard", "helmet", "poles", "boots"}


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
            if "full day price" in normalize_text(table.get_text(" ", strip=True))
        ),
        None,
    )
    if not table:
        raise ValueError("Could not find Equipment Rental Prices table")

    rows = table.find_all("tr")
    headers = [normalize_text(cell.get_text(" ", strip=True)) for cell in rows[0].find_all(["th", "td"])]
    full_day_index = next((index for index, header in enumerate(headers) if "full day price" in header), None)
    if full_day_index is None:
        raise ValueError("Could not find Full Day Price column")

    package_price = None
    items = {}
    for row in rows[1:]:
        cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["th", "td"])]
        if len(cells) <= full_day_index:
            continue
        label = normalize_text(cells[0])
        price = parse_price(cells[full_day_index])
        if price is None:
            continue
        if label == PACKAGE_NAME:
            package_price = price
        elif label == "skis":
            items["skis"] = price
        elif label == "snowboard":
            items["snowboard"] = price
        elif label == "poles or helmet":
            items["poles"] = price
            items["helmet"] = price
        elif label == "boots (snowboard or ski)":
            items["boots"] = price

    if package_price is None:
        raise ValueError(f"Could not find Full Day Price for {PACKAGE_NAME}")
    missing_items = REQUIRED_ITEMS - items.keys()
    if missing_items:
        raise ValueError(f"Missing Full Day rental items: {sorted(missing_items)}")
    return {
        "ski": {"adults": package_price, "youth": package_price},
        "snowboard": {"adults": package_price, "youth": package_price},
        "items": items,
    }


def main():
    payload = {
        "rentals": get_rentals(),
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
