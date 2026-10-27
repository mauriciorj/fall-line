import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.devilsglen.com"
PAGE_URL = f"{SOURCE_URL}/About/Ticket_Pricing"
RESORT_ID = "devils-glen"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}


def fetch_soup():
    response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser")


def normalize_text(value):
    return " ".join(value.lower().split())


def parse_price(value):
    match = re.search(r"\$\s*([0-9]+(?:[.,][0-9]+)?)", value)
    if not match:
        return None
    amount = float(match.group(1).replace(",", "."))
    return f"${int(amount) if amount.is_integer() else amount:g}"


def get_lift_rates():
    soup = fetch_soup()
    table = next(
        (
            table
            for table in soup.find_all("table")
            if "lift ticket type" in normalize_text(table.get_text(" ", strip=True))
        ),
        None,
    )
    if not table:
        raise ValueError("Could not find ticket pricing table")

    rates = {}
    rows = table.find_all("tr")
    for row in rows[1:]:
        cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["td", "th"])]
        if len(cells) < 3:
            continue
        label = normalize_text(cells[0])
        adult = parse_price(cells[1])
        student = parse_price(cells[2])
        if adult is None or student is None:
            continue
        if "full day weekend" in label:
            rates["day-weekend"] = {"adults": adult, "youth": student, "seniors": student}
        elif "full day midweek" in label:
            rates["day-week"] = {"adults": adult, "youth": student, "seniors": student}

    if not rates:
        raise ValueError("Could not parse ticket pricing")
    return rates


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
