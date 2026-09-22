import html
import json
import os
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

RESORT_ID = "calabogie-peaks"
SOURCE_URL = "https://calabogie.com/product/all-day-lift-tickets/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}
AGE_GROUPS = {"adult": "adults", "youth": "youth", "senior": "seniors"}


def normalize_text(value):
    return " ".join(value.lower().split())


def parse_price(value):
    amount = float(value)
    return f"${int(amount) if amount.is_integer() else amount:g}"


def get_lift_rates():
    response = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    selector = soup.select_one("select#age-group, select[name='attribute_age-group']")
    if not selector:
        raise ValueError("Could not find Age Group dropdown")
    age_options = {
        normalize_text(option.get_text(" ", strip=True)): option.get_text(" ", strip=True)
        for option in selector.find_all("option")
        if option.get("value")
    }

    form = soup.select_one("form.variations_form")
    if not form or not form.get("data-product_variations"):
        raise ValueError("Could not find Age Group variation prices")
    variations = json.loads(form["data-product_variations"])
    rates = {}
    for label in age_options:
        age_group = next((target for source, target in AGE_GROUPS.items() if source in label), None)
        if not age_group:
            continue
        variation = next(
            (
                item for item in variations
                if any(normalize_text(str(value)) == label for value in item.get("attributes", {}).values())
            ),
            None,
        )
        if variation is None or variation.get("display_price") is None:
            raise ValueError(f"Missing All Day Lift Ticket price for {label}")
        rates[age_group] = parse_price(variation["display_price"])

    missing = {"adults", "youth", "seniors"} - rates.keys()
    if missing:
        raise ValueError(f"Missing Age Group lift-ticket prices: {sorted(missing)}")
    return {"day-week": dict(rates), "day-weekend": dict(rates)}


def main():
    payload = {"rates": get_lift_rates(), "resortId": RESORT_ID, "sourceUrl": SOURCE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "lift-rates.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
