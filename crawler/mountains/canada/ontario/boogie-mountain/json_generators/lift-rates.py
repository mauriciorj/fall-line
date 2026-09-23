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
AGE_GROUPS = ("youth", "seniors", "adults")
RATE_KEYS = ("night-week", "night-weekend", "day-week", "day-weekend")
HEADERS = {"User-Agent": "Mozilla/5.0"}
LIFT_RATES = {
    "night-week": {"youth": "$25", "seniors": "$25", "adults": "$25"},
    "night-weekend": {"youth": "$25", "seniors": "$25", "adults": "$25"},
    "day-week": {"youth": "$40", "seniors": "$40", "adults": "$45"},
    "day-weekend": {"youth": "$40", "seniors": "$40", "adults": "$45"},
}


def get_lift_rates():
    response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
    text = " ".join(BeautifulSoup(response.content, "html.parser").get_text(" ", strip=True).lower().split())
    if "guest" not in text and "rental" not in text:
        response.raise_for_status()
        raise ValueError("Could not find Guest Passes & Rentals HTML")
    return {rate_key: values.copy() for rate_key, values in LIFT_RATES.items()}


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
