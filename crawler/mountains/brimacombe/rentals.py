import json
import os
import sys
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from convex_client import push_resort_rentals
from dtos import to_rentals_dto

URL = "https://brimacombe.ca/plan-your-visit/rentals/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
RESORT_ID = "brimacombe"

TABLE_SECTIONS = {
    0: "Individual Rental Packages",
    1: "Individual Rental Items",
    2: "7-Week Program Lesson Rentals",
}


def extract_table_data(table):
    """Extract table data into a list of dictionaries using thead as keys."""
    headers = []
    thead = table.find("thead")
    if thead:
        headers = [
            th.get_text(separator=" ", strip=True)
            for th in thead.find_all(["th", "td"])
        ]
    else:
        first_row = table.find("tr")
        if first_row:
            headers = [
                th.get_text(separator=" ", strip=True)
                for th in first_row.find_all(["th", "td"])
            ]

    rows = []
    data_rows = table.find_all("tr")[1:] if not thead else table.find_all("tr")
    for tr in data_rows:
        cells = tr.find_all("td")
        if not cells:
            continue
        values = [cell.get_text(separator=" ", strip=True) for cell in cells]
        if not any(values):
            continue
        if headers:
            row = {}
            for i, val in enumerate(values):
                key = headers[i] if i < len(headers) and headers[i] else f"Column_{i+1}"
                row[key] = val
            rows.append(row)
        else:
            rows.append(values)
    return rows


def get_rentals():
    """Fetch and parse rental prices from Brimacombe."""
    print(f"Fetching {URL}...")
    response = requests.get(URL, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    tables = soup.find_all("table")
    result = {}

    for i, table in enumerate(tables):
        section = TABLE_SECTIONS.get(i)
        if section is None:
            continue
        data = extract_table_data(table)
        if data:
            result[section] = data

    return result


def main():
    rentals = get_rentals()
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(rentals, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")

    result = push_resort_rentals(
        RESORT_ID,
        URL,
        to_rentals_dto(rentals),
        updated_at_ms=int(time.time() * 1000),
    )
    if result is not None:
        print("Pushed to Convex:", result)


if __name__ == "__main__":
    main()
