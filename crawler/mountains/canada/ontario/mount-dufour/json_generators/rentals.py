import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.mountdufour.com/"
PAGE_URL = "https://www.mountdufour.com/index.php/rentals"
RESORT_ID = "mount-dufour"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


def normalize_text(value):
    return " ".join(value.replace("\xa0", " ").split()).lower()


def parse_price(value):
    match = re.search(r"\$\s*([0-9]+(?:[.,][0-9]+)?)", value)
    if not match:
        raise ValueError(f"Could not parse rental price: {value}")
    amount = float(match.group(1).replace(",", "."))
    return f"${int(amount) if amount.is_integer() else amount:g}"


def parse_table(table):
    rows = table.find_all("tr")
    headers = [normalize_text(cell.get_text(" ", strip=True)) for cell in rows[0].find_all(["th", "td"])]
    try:
        full_day_index = headers.index("full day")
    except ValueError as error:
        raise ValueError("Could not find Full Day rental column") from error
    values = {}
    for row in rows[1:]:
        cells = row.find_all(["th", "td"])
        if len(cells) <= full_day_index:
            continue
        values[normalize_text(cells[0].get_text(" ", strip=True))] = parse_price(cells[full_day_index].get_text(" ", strip=True))
    return values


def get_rentals():
    response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    tables = soup.find_all("table")
    ski_table = next((table for table in tables if "ski rentals" in normalize_text(table.find("tr").get_text(" ", strip=True))), None)
    snowboard_table = next((table for table in tables if "snowboard rentals" in normalize_text(table.find("tr").get_text(" ", strip=True))), None)
    if not ski_table or not snowboard_table:
        raise ValueError("Could not find ski or snowboard rental tables")

    ski = parse_table(ski_table)
    snowboard = parse_table(snowboard_table)
    rentals = {
        "ski": {
            "adults": ski["ski package (skis, boots, poles)"],
            "youth": ski["ski package (age 12 and under)"],
        },
        "snowboard": {
            "adults": snowboard["full package (board and boots)"],
            "youth": snowboard["full package (age 12 and under)"],
        },
        "items": {
            "skis": ski["skis only"],
            "snowboard": snowboard["board only"],
            "boots": ski["boots only"],
            "poles": ski["poles only"],
        },
    }
    return rentals


def main():
    payload = {"rentals": get_rentals(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
