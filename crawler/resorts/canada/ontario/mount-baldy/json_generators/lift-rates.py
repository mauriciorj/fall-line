import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.skimountbaldy.ca/"
PAGE_URL = "https://www.skimountbaldy.ca/tickets-and-passes"
RESORT_ID = "mount-baldy"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}
PRICE_ROWS = {
    "saturday/sunday full day": "day-weekend",
    "weekend half day & holiday rate": "day-week",
    "friday night skiing": "night-week",
    "saturday night skiing": "night-weekend",
}


def normalize_text(value):
    value = value.replace("\xa0", " ").replace("\ufeff", "").replace("\u200b", "")
    return " ".join(value.split()).lower()


def normalize_price(value):
    match = re.search(r"\$?\s*[\d,.]+", value)
    if not match:
        raise ValueError(f"Could not parse price: {value}")
    return "$" + re.sub(r"[^\d,.]", "", match.group(0))


def get_lift_rates():
    response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    heading = next(
        (
            element
            for element in soup.find_all(["h2", "h3", "h4"])
            if normalize_text(element.get_text(" ", strip=True)) == "day tickets"
        ),
        None,
    )
    if not heading:
        raise ValueError("Could not find Day Tickets section")
    table = heading.find_next("table")
    if not table:
        raise ValueError("Could not find Day Tickets table")

    header = next(
        (
            row
            for row in table.find_all("tr")
            if "adult" in [normalize_text(cell.get_text(" ", strip=True)) for cell in row.find_all(["th", "td"])]
        ),
        None,
    )
    if not header:
        raise ValueError("Could not find Adult price column")
    headers = [normalize_text(cell.get_text(" ", strip=True)) for cell in header.find_all(["th", "td"])]
    adult_index = headers.index("adult")
    rates = {}
    for row in table.find_all("tr"):
        cells = row.find_all(["th", "td"])
        if len(cells) <= adult_index or row is header:
            continue
        label = normalize_text(cells[0].get_text(" ", strip=True))
        rate_key = next((key for row_label, key in PRICE_ROWS.items() if label.startswith(row_label)), None)
        if rate_key:
            rates[rate_key] = {"adults": normalize_price(cells[adult_index].get_text(" ", strip=True))}

    missing = set(PRICE_ROWS.values()) - rates.keys()
    if missing:
        raise ValueError(f"Missing Day Tickets rates: {sorted(missing)}")
    return rates


def main():
    payload = {"rates": get_lift_rates(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "lift-rates.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
