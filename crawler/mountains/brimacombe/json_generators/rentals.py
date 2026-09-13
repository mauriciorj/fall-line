import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

URL = "https://brimacombe.ca/plan-your-visit/rentals/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}
RESORT_ID = "brimacombe"
TABLE_SECTIONS = {
    0: "Individual Rental Packages",
    1: "Individual Rental Items",
    2: "7-Week Program Lesson Rentals",
}


def parse_price(value):
    if value in (None, ""):
        return None
    match = re.search(r"\$?\s*(\d+(?:[.,]\d+)?)", str(value))
    if not match:
        return None
    amount = float(match.group(1).replace(",", "."))
    return f"${int(amount) if amount.is_integer() else amount:g}"


def extract_table_data(table):
    headers = []
    thead = table.find("thead")
    if thead:
        headers = [
            cell.get_text(separator=" ", strip=True)
            for cell in thead.find_all(["th", "td"])
        ]
    else:
        first_row = table.find("tr")
        if first_row:
            headers = [
                cell.get_text(separator=" ", strip=True)
                for cell in first_row.find_all(["th", "td"])
            ]

    rows = []
    data_rows = table.find_all("tr")[1:] if not thead else table.find_all("tr")
    for row_element in data_rows:
        cells = row_element.find_all(["td", "th"])
        values = [cell.get_text(separator=" ", strip=True) for cell in cells]
        if not values or not any(values):
            continue
        rows.append(
            {
                headers[index]
                if index < len(headers) and headers[index]
                else f"Column_{index + 1}": value
                for index, value in enumerate(values)
            }
        )
    return rows


def get_rentals():
    print(f"Fetching {URL}...")
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    tables = soup.find_all("table")
    result = {}
    for index, table in enumerate(tables):
        section = TABLE_SECTIONS.get(index)
        if section is None:
            continue
        data = extract_table_data(table)
        if data:
            result[section] = data
    return result


def get_row_name(row):
    name_key = next(
        (
            key
            for key in row
            if key.lower() in {"name", "item"}
            or "package" in key.lower()
            or "rental item" in key.lower()
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


def get_adult_item_price(row, name_key):
    for label, value in row.items():
        if "age" in label.lower() and "14" in label.lower():
            parsed = parse_price(value)
            if parsed is not None:
                return parsed
    return get_first_price(row, name_key)


def normalize_rentals(rentals):
    result = {
        "ski": {},
        "snowboard": {},
        "items": {"boots": "$", "helmet": "$", "ice skate": "$", "skis": "$", "snowboard": "$", "poles": "$"},
    }

    for section_name, rows in rentals.items():
        section = section_name.lower()
        for row in rows:
            name, name_key = get_row_name(row)
            normalized_name = name.lower()
            price = get_first_price(row, name_key)

            if "individual rental package" in section and price is not None:
                if "13 & under" in normalized_name:
                    result["ski"]["youth"] = price
                    result["snowboard"]["youth"] = price
                elif "ages 14" in normalized_name:
                    result["ski"]["adults"] = price
                    result["snowboard"]["adults"] = price

            if "individual rental item" in section or "2026-27 individual item" in section:
                item_price = get_adult_item_price(row, name_key)
                if item_price is None:
                    continue
                if "boot" in normalized_name:
                    result["items"]["boots"] = item_price
                elif "helmet" in normalized_name:
                    result["items"]["helmet"] = item_price
                elif "ice skate" in normalized_name or "skate" in normalized_name:
                    result["items"]["ice skate"] = item_price
                elif "ski" in normalized_name and "snowboard" in normalized_name:
                    result["items"]["skis"] = item_price
                    result["items"]["snowboard"] = item_price
                elif "ski" in normalized_name:
                    result["items"]["skis"] = item_price
                elif "snowboard" in normalized_name:
                    result["items"]["snowboard"] = item_price
                elif "pole" in normalized_name:
                    result["items"]["poles"] = item_price

    missing = [
        f"{section}.{age_group}"
        for section in ("ski", "snowboard")
        for age_group in ("youth", "adults")
        if age_group not in result[section]
    ]
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
