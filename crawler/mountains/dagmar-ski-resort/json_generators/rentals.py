"""Dagmar rental rates crawler."""

import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

URL = "https://www.skidagmar.com/alpine-rates/"
RESORT_ID = "dagmar-ski-resort"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
}


def extract_table_data(table):
    headers = [
        cell.get_text(" ", strip=True)
        for cell in table.find("thead").find_all(["th", "td"])
    ] if table.find("thead") else []
    rows = table.find("tbody").find_all("tr") if table.find("tbody") else table.find_all("tr")
    result = []
    for row in rows:
        cells = row.find_all(["td", "th"])
        values = [cell.get_text(" ", strip=True) for cell in cells]
        if not values or not any(values) or values == headers:
            continue
        result.append(
            {
                headers[index]
                if index < len(headers) and headers[index]
                else f"Column_{index + 1}": value
                for index, value in enumerate(values)
            }
        )
    return result


def get_rentals():
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    tables = BeautifulSoup(response.content, "html.parser").find_all("table", class_="table")
    result = {}
    for index, table in enumerate(tables):
        rows = extract_table_data(table)
        if rows:
            heading = table.find_previous(["h2", "h3", "h4", "h5"])
            section = heading.get_text(" ", strip=True) if heading else f"Rental_Rates_{index + 1}"
            result[section] = rows
    return result


def parse_price(value):
    if value in (None, ""):
        return None
    match = re.search(r"\$?\s*(\d+(?:[.,]\d+)?)", str(value))
    if not match:
        return None
    amount = float(match.group(1).replace(",", "."))
    return f"${int(amount) if amount.is_integer() else amount:g}"


def get_row_name(row):
    name_key = next(
        (
            key
            for key in row
            if key.lower() in {"name", "item", "category", "rental"}
        ),
        next(iter(row), "name"),
    )
    return str(row.get(name_key, "")), name_key


def get_first_price(row, excluded_key=None):
    for label, value in row.items():
        if label == excluded_key:
            continue
        parsed = parse_price(value)
        if parsed is not None:
            return parsed
    return None


def normalize_rentals(rentals):
    result = {
        "ski": {},
        "snowboard": {},
        "items": {},
    }
    package_price = None

    for section_name, rows in rentals.items():
        section_text = section_name.lower()
        for row in rows:
            name, name_key = get_row_name(row)
            text = f"{section_text} {name.lower()}"
            price = get_first_price(row, name_key)
            if price is None:
                continue

            if "equipment rentals" in text and "all ages" in text and "full day" in text:
                package_price = price
                continue

            if "separate items" not in section_text and "individual" not in section_text:
                continue
            normalized_name = name.lower()
            if "boot" in normalized_name:
                result["items"]["boots"] = price
            elif "ski" in normalized_name and "snowboard" in normalized_name:
                result["items"]["skis"] = price
                result["items"]["snowboard"] = price
            elif "ski" in normalized_name:
                result["items"]["skis"] = price
            elif "snowboard" in normalized_name:
                result["items"]["snowboard"] = price
            elif "pole" in normalized_name:
                result["items"]["poles"] = price
            elif "helmet" in normalized_name:
                result["items"]["helmet"] = price

    if package_price is not None:
        result["ski"] = {"youth": package_price, "adults": package_price}
        result["snowboard"] = {"youth": package_price, "adults": package_price}

    required_items = ("boots", "skis", "snowboard", "poles", "helmet")
    missing = [
        key
        for key in ("ski", "snowboard", *required_items)
        if key not in result.get("items", {}) and key not in result
    ]
    if package_price is None:
        missing.extend(["ski", "snowboard"])
    if missing:
        print(f"Missing rental values: {', '.join(missing)}")
        return None
    return result


def main():
    rentals = normalize_rentals(get_rentals())
    if rentals is None:
        return
    payload = {
        "rentals": rentals,
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
