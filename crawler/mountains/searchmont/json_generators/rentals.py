import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://searchmont.com/"
PAGE_URL = "https://searchmont.com/rentals/"
RESORT_ID = "searchmont"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


def normalize_text(value):
    return " ".join(value.replace("\xa0", " ").split()).lower()


def parse_price(value):
    match = re.search(r"\$\s*([0-9]+(?:[.,][0-9]+)?)", value)
    if not match:
        raise ValueError(f"Could not parse rental price: {value}")
    amount = float(match.group(1).replace(",", "."))
    return f"${int(amount) if amount.is_integer() else amount:g}"


def extract_price(text, label):
    match = re.search(rf"{label}\s+(\$\s*[0-9]+(?:[.,][0-9]+)?)", text, re.IGNORECASE)
    if not match:
        raise ValueError(f"Could not find rental price for {label}")
    return parse_price(match.group(1))


def get_rentals():
    response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    text = normalize_text(BeautifulSoup(response.content, "html.parser").get_text(" ", strip=True))
    regular = extract_price(text, r"rental package\s+regular")
    youth = extract_price(text, r"rental package\s+12 & under")
    helmet = extract_price(text, r"\bhelmet\b")
    poles = extract_price(text, r"\bpoles\b")
    snowshoes = extract_price(text, r"\bsnowshoes\b")
    return {
        "ski": {"adults": regular, "youth": youth},
        "snowboard": {"adults": regular, "youth": youth},
        "items": {"helmet": helmet, "poles": poles, "snowshoes": snowshoes},
    }


def main():
    payload = {"rentals": get_rentals(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
