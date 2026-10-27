import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

RESORT_ID = "antoine-mountain"
SOURCE_URL = "https://antoinemountain.ca/pages/rentals"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


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
    result = {"ski": {}, "snowboard": {}, "items": {}}
    for cell in soup.find_all("td"):
        cell_text = cell.get_text(" ", strip=True)
        price = parse_price(cell_text)
        if price is None:
            continue
        label_element = cell.find("strong")
        label = normalize_text(label_element.get_text(" ", strip=True) if label_element else cell_text)
        label = normalize_text(re.sub(r"\$\s*[0-9]+(?:[.,][0-9]+)?", "", label))
        if "ski (skis, boots, poles" in label:
            result["ski"] = {"adults": price, "youth": price}
        elif "snowboard (board, boots" in label:
            result["snowboard"] = {"adults": price, "youth": price}
        elif label.startswith("skis only"):
            result["items"]["skis"] = price
        elif label.startswith("board"):
            result["items"]["snowboard"] = price
        elif label.startswith("poles only"):
            result["items"]["poles"] = price
        elif label.startswith("boots (sizes: childs 9.5"):
            result["items"]["boots"] = price
        elif label.startswith("helmet only"):
            result["items"]["helmet"] = price

    missing = [section for section in ("ski", "snowboard") if not result[section]]
    missing.extend(item for item in ("skis", "snowboard", "poles", "boots", "helmet") if item not in result["items"])
    if missing:
        raise ValueError(f"Missing rental values: {missing}")
    return result


def main():
    payload = {"rentals": get_rentals(), "resortId": RESORT_ID, "sourceUrl": SOURCE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
