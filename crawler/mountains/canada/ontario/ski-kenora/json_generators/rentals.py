import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

PAGE_URL = "https://www.skikenora.ca/downhill/#rental-equipment"
RESORT_ID = "ski-kenora"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


def normalize_text(value):
    return " ".join(value.lower().split())


def extract_price(text, label):
    match = re.search(rf"{label}\s*:\s*\$\s*([0-9]+(?:\.[0-9]+)?)", text, re.IGNORECASE)
    if not match:
        raise ValueError(f"Could not find rental price for {label}")
    return f"${match.group(1)}"


def get_rentals():
    response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    text = normalize_text(BeautifulSoup(response.content, "html.parser").get_text(" ", strip=True))
    youth = extract_price(text, r"youth\s*\(13-17\)\s*full\s*day")
    adult = extract_price(text, r"adult\s*full\s*day")
    rental_prices = {"adults": adult, "youth": youth}
    return {"ski": rental_prices.copy(), "snowboard": rental_prices.copy(), "items": {}}


def main():
    payload = {"rentals": get_rentals(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
