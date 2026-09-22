import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.sirsams.ca/"
PAGE_URL = "https://www.sirsams.ca/winter/rentals"
RESORT_ID = "sir-sams"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


def normalize_text(value):
    return " ".join(value.replace("\xa0", " ").split()).lower()


def parse_price(value):
    match = re.search(r"\$\s*([0-9]+(?:[.,][0-9]+)?)", value)
    if not match:
        raise ValueError(f"Could not parse rental price: {value}")
    amount = float(match.group(1).replace(",", "."))
    return f"${int(amount) if amount.is_integer() else amount:g}"


def get_section_prices(headings, start_marker, end_marker):
    start = next((index for index, heading in enumerate(headings) if start_marker in normalize_text(heading.get_text(" ", strip=True))), None)
    if start is None:
        raise ValueError(f"Could not find {start_marker} section")
    end = next((index for index in range(start + 1, len(headings)) if end_marker in normalize_text(headings[index].get_text(" ", strip=True))), len(headings))
    prices = [parse_price(heading.get_text(" ", strip=True)) for heading in headings[start:end] if re.search(r"\$\s*[0-9]+", heading.get_text(" ", strip=True))]
    if len(prices) < 16:
        raise ValueError(f"Could not find Full Day rental prices for {start_marker}")
    return prices


def get_rentals():
    response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    prices = get_section_prices(headings, "weekend & holiday pricing", "midweek pricing")
    package_price = prices[1]
    item_price = {"skis": prices[9], "snowboard": prices[9], "boots": prices[13], "helmet": prices[14], "poles": prices[15]}
    rentals = {
        "ski": {"adults": package_price, "youth": package_price},
        "snowboard": {"adults": package_price, "youth": package_price},
        "items": item_price,
    }
    return rentals


def main():
    payload = {"rentals": get_rentals(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
