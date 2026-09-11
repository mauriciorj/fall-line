"""Lake Ridge rental rates crawler."""

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

URL = "https://ski-lakeridge.com/skiing-snowboarding/equipment-rentals/"
RESORT_ID = "lakeridge-ski-resort"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def extract_table_data(table, include_adult=False):
    rows = table.find_all("tr")
    if not rows:
        return []
    headers = [cell.get_text(" ", strip=True) for cell in rows[0].find_all(["th", "td"])]
    headers = [header or f"Column_{index + 1}" for index, header in enumerate(headers)]
    result = []
    for row in rows[1:]:
        cells = row.find_all("td")
        if not cells:
            continue
        values = [cell.get_text(" ", strip=True) for cell in cells]
        values.extend([""] * max(0, len(headers) - len(values)))
        result.append({headers[index]: values[index] for index in range(min(len(headers), len(values)))})
    if include_adult and result:
        name_key = next(
            (
                key
                for key in result[0]
                if key.lower() in {"name", "item", "category", "description", "time"}
            ),
            next(iter(result[0]), "name"),
        )
        adult = {name_key: "ADULT"}
        adult.update({header: header for header in headers if header != name_key})
        result.insert(0, adult)
    return result


def get_rentals():
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    result = {}
    adult_package_sections = {
        "skis, boots and poles package",
        "snowboard and boots package",
    }
    for index, table in enumerate(soup.find_all("table"), 1):
        heading = table.find_previous(["h2", "h3", "h4"])
        section_name = heading.get_text(" ", strip=True) if heading else f"Rentals_{index}"
        normalized_name = " ".join(section_name.split()).lower()
        rows = extract_table_data(table, normalized_name in adult_package_sections)
        if rows:
            result[section_name] = rows
    return result


def main():
    payload = {
        "rentals": to_rentals_dto(get_rentals()),
        "resortId": RESORT_ID,
        "sourceUrl": URL,
        "updatedAt": int(time.time() * 1000),
    }
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
