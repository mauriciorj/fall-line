import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup, NavigableString

SOURCE_URL = "https://www.lochlomond.ca/"
PAGE_URL = "https://www.lochlomond.ca/rentals/equipment-rental/"
RESORT_ID = "loch-lomond"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


def normalize_text(value):
    return " ".join(value.replace("\xa0", " ").split())


def get_rental_prices_text(soup):
    heading = next(
        (
            element
            for element in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
            if normalize_text(element.get_text(" ", strip=True)).lower() == "rental prices"
        ),
        None,
    )
    if not heading:
        raise ValueError("Could not find Rental Prices section")

    level = int(heading.name[1])
    content = []
    for node in heading.next_elements:
        if getattr(node, "name", None) and re.fullmatch(r"h[1-6]", node.name) and int(node.name[1]) <= level:
            break
        if isinstance(node, NavigableString):
            content.append(str(node))
    return normalize_text(" ".join(content))


def get_price(text, label):
    match = re.search(rf"{label}\s*(\$\s*[\d,.]+)", text, re.IGNORECASE)
    if not match:
        raise ValueError(f"Could not find rental price for {label}")
    return normalize_text(match.group(1)).replace(" ", "")


def get_rentals():
    response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    text = get_rental_prices_text(soup)
    ski_price = get_price(text, r"ski\s*/\s*snowboard\s+full\s+set")
    snowboard_price = get_price(text, r"skis\s*/\s*board\s+only")
    snowshoes_price = get_price(text, r"snowshoes")
    return {
        "ski": {"adults": ski_price, "youth": ski_price},
        "snowboard": {"adults": snowboard_price, "youth": snowboard_price},
        "items": {"snowshoes": snowshoes_price},
    }


def main():
    payload = {"rentals": get_rentals(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
