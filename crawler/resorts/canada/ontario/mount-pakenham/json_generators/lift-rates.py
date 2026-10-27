import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://shop.mountpakenham.com/"
PAGE_URL = "https://shop.mountpakenham.com/pages/skiing-snowboarding"
RESORT_ID = "mount-pakenham"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


def normalize_text(value):
    return " ".join(value.replace("\xa0", " ").split()).lower()


def normalize_price(value):
    match = re.search(r"\$?\s*[\d,.]+", value)
    if not match:
        raise ValueError(f"Could not parse price: {value}")
    return "$" + re.sub(r"[^\d,.]", "", match.group(0))


def categorized_rate(price):
    return {"adults": price, "youth": price, "seniors": price}


def get_lift_rates():
    response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    daily_table = next((table for table in soup.find_all("table") if "open - close" in normalize_text(table.get_text(" ", strip=True))), None)
    night_table = next((table for table in soup.find_all("table") if "night ticket" in normalize_text(table.get_text(" ", strip=True))), None)
    if not daily_table or not night_table:
        raise ValueError("Could not find Daily Lift Rates or Night Ticket table")

    daily_rates = {}
    column_index = 1
    category = None
    for row in daily_table.find_all("tr"):
        cells = row.find_all(["th", "td"])
        values = [normalize_text(cell.get_text(" ", strip=True)) for cell in cells]
        if not values:
            continue
        if values[0] in ("weekend/holiday*", "weekday"):
            category = values[0]
            continue
        if category and values[0].startswith("adult") and len(values) > column_index:
            daily_rates[category] = categorized_rate(normalize_price(values[column_index]))

    night_row = night_table.find("tr")
    night_cells = night_row.find_all(["th", "td"]) if night_row else []
    if len(night_cells) < 2:
        raise ValueError("Could not find Night Ticket price")
    night_price = categorized_rate(normalize_price(night_cells[1].get_text(" ", strip=True)))
    if "weekday" not in daily_rates or "weekend/holiday*" not in daily_rates:
        raise ValueError("Missing Daily Lift Rates adult prices")
    return {
        "day-week": daily_rates["weekday"],
        "day-weekend": daily_rates["weekend/holiday*"],
        "night-week": night_price.copy(),
        "night-weekend": night_price.copy(),
    }


def main():
    payload = {"rates": get_lift_rates(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "lift-rates.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
