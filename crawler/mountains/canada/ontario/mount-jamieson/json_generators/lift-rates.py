import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.mountjamieson.ca/"
PAGE_URL = "https://www.mountjamieson.ca/day-passes"
RESORT_ID = "mount-jamieson"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


def normalize_text(value):
    return " ".join(value.replace("\xa0", " ").split()).lower()


def get_day_passes_text(soup):
    blocks = soup.select(".sqs-html-content")
    start = next(
        (
            index
            for index, block in enumerate(blocks)
            if normalize_text(block.get_text(" ", strip=True)) == "day passes"
        ),
        None,
    )
    if start is None:
        raise ValueError("Could not find DAY PASSES section")

    content = []
    for block in blocks[start + 1:]:
        value = normalize_text(block.get_text(" ", strip=True))
        if value == "half-day passes":
            break
        content.append(value)
    return " ".join(content)


def get_price(text, label):
    match = re.search(rf"{label}.*?(\$\s*[\d,.]+)", text, re.IGNORECASE)
    if not match:
        raise ValueError(f"Could not find Day Pass price for {label}")
    return "$" + re.sub(r"[^\d,.]", "", match.group(1))


def get_lift_rates():
    response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    text = get_day_passes_text(soup)
    rates = {
        "adults": get_price(text, r"adult\s+18\s*\+"),
        "youth": get_price(text, r"youth\s*:\s*13\s*[-–]\s*17"),
        "seniors": get_price(text, r"senior\s*[-–]\s*60\+"),
    }
    return {"day-week": rates.copy(), "day-weekend": rates.copy()}


def main():
    payload = {"rates": get_lift_rates(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "lift-rates.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
