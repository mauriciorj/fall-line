import json
import os
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

PAGE_URL = "https://www.batawaskihill.com/lift-tickets"
RESORT_ID = "batawa-ski-hill"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def get_lift_rates():
    response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    text = " ".join(BeautifulSoup(response.content, "html.parser").get_text(" ", strip=True).split()).lower()
    if "lift" not in text or "ticket" not in text:
        raise ValueError("Could not verify lift tickets HTML")
    return {}


def main():
    payload = {
        "rates": get_lift_rates(),
        "resortId": RESORT_ID,
        "sourceUrl": PAGE_URL,
        "updatedAt": int(time.time() * 1000),
    }
    output_file = os.path.join(os.path.dirname(__file__), "lift-rates.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
