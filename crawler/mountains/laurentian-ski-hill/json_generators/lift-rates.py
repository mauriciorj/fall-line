import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

RESORT_ID = "laurentian-ski-hill-north-bay"
SOURCE_URL = "https://laurentianskihill.com/rates/lift-tickets/"
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


def get_lift_rates():
    response = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.select_one('table[aria-label="Lift Ticket Pricing"]')
    if not table:
        raise ValueError("Could not find Lift Ticket Pricing table")

    headers = [normalize_text(cell.get_text(" ", strip=True)) for cell in table.select("thead th")]
    full_day_index = next((index for index, header in enumerate(headers) if "full day" in header and "any 8 hours" in header), None)
    if full_day_index is None:
        raise ValueError("Could not find Full Day (Any 8 Hours) column")

    rates = {}
    for row in table.select("tbody tr"):
        cells = row.find_all(["th", "td"])
        if len(cells) <= full_day_index:
            continue
        label = normalize_text(cells[0].get_text(" ", strip=True))
        if "children day pass" in label and "ages 6-12" in label:
            age_group = "youth"
        elif label == "adult":
            age_group = "adults"
        else:
            continue
        price = parse_price(cells[full_day_index].get_text(" ", strip=True))
        if price:
            rates[age_group] = price

    if "youth" not in rates or "adults" not in rates:
        raise ValueError("Missing Full Day (Any 8 Hours) youth or adult price")
    rates["seniors"] = rates["adults"]
    return {"day-week": dict(rates), "day-weekend": dict(rates)}


def main():
    payload = {"rates": get_lift_rates(), "resortId": RESORT_ID, "sourceUrl": SOURCE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "lift-rates.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
