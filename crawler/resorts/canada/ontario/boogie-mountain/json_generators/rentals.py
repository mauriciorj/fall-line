import json
import os
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://boogiemountain.com/"
PAGE_URL = "https://boogiemountain.com/guest-passes-rentals/"
RESORT_ID = "boogie-mountain"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def get_rentals():
    response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
    text = " ".join(BeautifulSoup(response.content, "html.parser").get_text(" ", strip=True).lower().split())
    if "rental equipment" not in text:
        response.raise_for_status()
        raise ValueError("Could not find Rental Equipment HTML")
    return {
        "ski": {"youth": "$20", "adults": "$20"},
        "snowboard": {"youth": "$20", "adults": "$20"},
        "items": {},
    }


def main():
    payload = {
        "rentals": get_rentals(),
        "resortId": RESORT_ID,
        "sourceUrl": PAGE_URL,
        "updatedAt": int(time.time() * 1000),
    }
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
