import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.mountdufour.com/"
PAGE_URL = "https://www.mountdufour.com/index.php/ski-conditions/ticket-prices"
RESORT_ID = "mount-dufour"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


def normalize_text(value):
    return " ".join(value.replace("\xa0", " ").split()).lower()


def parse_price(value):
    match = re.search(r"\$\s*([0-9]+(?:[.,][0-9]+)?)", value)
    if not match:
        raise ValueError(f"Could not parse ticket price: {value}")
    amount = float(match.group(1).replace(",", "."))
    return f"${int(amount) if amount.is_integer() else amount:g}"


def get_lift_rates():
    response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    table = next(
        (
            table
            for table in soup.find_all("table")
            if "full day" in normalize_text(table.get_text(" ", strip=True))
            and "half day" in normalize_text(table.get_text(" ", strip=True))
        ),
        None,
    )
    if not table:
        raise ValueError("Could not find Full Day ticket prices table")

    rates = {}
    for row in table.find_all("tr"):
        cells = row.find_all(["th", "td"])
        if len(cells) < 2:
            continue
        label = normalize_text(cells[0].get_text(" ", strip=True))
        price_text = cells[1].get_text(" ", strip=True)
        if not re.search(r"\$\s*[0-9]+", price_text):
            continue
        price = parse_price(price_text)
        if label.startswith("adult"):
            rates["adults"] = price
        elif label.startswith("seniors"):
            rates["seniors"] = price
        elif label.startswith("teens"):
            rates["youth"] = price

    missing = {"adults", "youth", "seniors"} - rates.keys()
    if missing:
        raise ValueError(f"Missing Full Day ticket rates: {sorted(missing)}")
    return {"day-week": rates.copy(), "day-weekend": rates.copy()}


def main():
    payload = {"rates": get_lift_rates(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "lift-rates.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
