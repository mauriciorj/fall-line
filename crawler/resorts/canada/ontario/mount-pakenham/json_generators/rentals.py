import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://shop.mountpakenham.com/"
PAGE_URL = "https://shop.mountpakenham.com/pages/equipment-rental"
RESORT_ID = "mount-pakenham"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


def normalize_text(value):
    return " ".join(value.replace("\xa0", " ").split()).lower()


def normalize_price(value):
    match = re.search(r"\$?\s*[\d,.]+", value)
    if not match:
        raise ValueError(f"Could not parse rental price: {value}")
    return "$" + re.sub(r"[^\d,.]", "", match.group(0))


def get_rentals():
    response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    table = next(
        (
            table
            for table in soup.find_all("table")
            if "rental equipment type" in normalize_text(table.get_text(" ", strip=True))
            and "fee" in normalize_text(table.get_text(" ", strip=True))
        ),
        None,
    )
    if not table:
        raise ValueError("Could not find Rental Equipment Type table")

    prices = {}
    for row in table.find_all("tr"):
        cells = row.find_all(["th", "td"])
        if len(cells) < 2:
            continue
        label = normalize_text(cells[0].get_text(" ", strip=True))
        if label.startswith("skis/boots/poles/helmet"):
            prices["ski_package"] = normalize_price(cells[1].get_text(" ", strip=True))
        elif label.startswith("snowboard/boots/helmet"):
            prices["snowboard_package"] = normalize_price(cells[1].get_text(" ", strip=True))
        elif label == "poles only":
            prices["poles"] = normalize_price(cells[1].get_text(" ", strip=True))
        elif label == "helmet only":
            prices["helmet"] = normalize_price(cells[1].get_text(" ", strip=True))
        elif label.startswith("snowshoes (+ trail pass)"):
            prices["snowshoes"] = normalize_price(cells[1].get_text(" ", strip=True))

    missing = {"ski_package", "snowboard_package", "poles", "helmet", "snowshoes"} - prices.keys()
    if missing:
        raise ValueError(f"Missing rental prices: {sorted(missing)}")
    return {
        "ski": {"adults": prices["ski_package"], "youth": prices["ski_package"]},
        "snowboard": {"adults": prices["snowboard_package"], "youth": prices["snowboard_package"]},
        "items": {
            "poles": prices["poles"],
            "helmet": prices["helmet"],
            "snowshoes": prices["snowshoes"],
        },
    }


def main():
    payload = {"rentals": get_rentals(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
