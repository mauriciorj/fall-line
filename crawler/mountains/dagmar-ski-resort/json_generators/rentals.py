"""Dagmar rental rates crawler."""

import json
import os
import sys
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dtos import to_rentals_dto

URL = "https://www.skidagmar.com/alpine-rates/"
RESORT_ID = "dagmar-ski-resort"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
TABLE_SECTIONS = {5: "Equipment Rentals - Package", 6: "Equipment Rentals - Separate Items", 7: "Lockers"}


def extract_table_data(table):
    rows = table.find("tbody").find_all("tr") if table.find("tbody") else table.find_all("tr")
    headers = [cell.get_text(" ", strip=True) for cell in table.find("thead").find_all(["th", "td"])] if table.find("thead") else []
    result = []
    for row in rows:
        cells = row.find_all("td")
        values = [cell.get_text(" ", strip=True) for cell in cells]
        if not values or not any(values):
            continue
        result.append({headers[index] if index < len(headers) and headers[index] else f"Column_{index + 1}": value for index, value in enumerate(values)})
    return result


def get_rentals():
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    tables = BeautifulSoup(response.content, "html.parser").find_all("table", class_="table")
    return {section: rows for index, table in enumerate(tables) if (section := TABLE_SECTIONS.get(index)) and (rows := extract_table_data(table))}


def main():
    payload = {"rentals": to_rentals_dto(get_rentals()), "resortId": RESORT_ID, "sourceUrl": URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
