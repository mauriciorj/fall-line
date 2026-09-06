import json
import re
import os
import sys
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from convex_client import push_resort_rates
from dtos import to_rates_dto

URL = "https://www.skidagmar.com/alpine-rates/"
RESORT_ID = "dagmar-ski-resort"
RESORT_NAME = "Dagmar Ski Resort"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Mapping of table index to the h3 section it belongs under (lift tickets only)
TABLE_SECTIONS = {
    0: "8 Pack Value-Priced Lift Tickets",
    1: "Anytime Alpine Lift Tickets",
    2: "Special Late-Night After 6 and Last Call",
    3: "Magic Carpet Special for Beginners",
    4: "Seniors 60+",
}


def extract_table_data(table):
    """Extract table rows into a list of dictionaries using thead as keys."""
    headers = []
    thead = table.find("thead")
    if thead:
        headers = [
            th.get_text(strip=True) for th in thead.find_all(["th", "td"])
        ]

    rows = []
    for tr in table.find("tbody").find_all("tr") if table.find("tbody") else table.find_all("tr"):
        cells = tr.find_all("td")
        if not cells:
            continue
        values = [cell.get_text(strip=True) for cell in cells]
        # Skip completely empty rows
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


def get_rates():
    """Fetch and parse all rates from Ski Dagmar."""
    print(f"Fetching {URL}...")
    response = requests.get(URL, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    tables = soup.find_all("table", class_="table")
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
    rates = get_rates()
    output_file = os.path.join(os.path.dirname(__file__), "lift-rates.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(rates, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")

    push_result = push_resort_rates(
        RESORT_ID,
        RESORT_NAME,
        URL,
        to_rates_dto(rates),
        fetched_at_ms=int(time.time() * 1000),
    )
    if push_result is not None:
        print("Pushed to Convex:", push_result)


if __name__ == "__main__":
    main()
