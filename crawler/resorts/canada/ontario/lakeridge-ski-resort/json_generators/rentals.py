"""Lakeridge rental rates crawler."""

import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

URL = "https://ski-lakeridge.com/skiing-snowboarding/equipment-rentals/"
RESORT_ID = "lakeridge-ski-resort"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
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
    rows = table.find_all("tr")
    if not rows:
        return []
    headers = [cell.get_text(" ", strip=True) for cell in rows[0].find_all(["th", "td"])]
    result = []
    for row in rows[1:]:
        cells = row.find_all("td")
        if not cells:
            continue
        values = [cell.get_text(" ", strip=True) for cell in cells]
        values.extend([""] * max(0, len(headers) - len(values)))
        result.append(
            {
                headers[index] or f"Column_{index + 1}": values[index]
                for index in range(min(len(headers), len(values)))
            }
        )
    return result


def get_rentals():
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    result = {}
    for index, table in enumerate(soup.find_all("table"), 1):
        heading = table.find_previous(["h2", "h3", "h4"])
        section_name = heading.get_text(" ", strip=True) if heading else f"Rentals_{index}"
        rows = extract_table_data(table)
        if rows:
            result[section_name] = rows
    return result


def get_row_name(row):
    name_key = next(
        (
            key
            for key in row
            if key.lower() in {"name", "item", "category", "description"}
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
        "items": {"boots": "$", "helmet": "$", "ice-skates": "$", "poles": "$", "skis": "$", "snowboard": "$"},
    }

    for section_name, rows in rentals.items():
        section = section_name.lower()
        for row in rows:
            name, name_key = get_row_name(row)
            normalized_name = name.lower()
            price = get_first_price(row, name_key)
            if price is None:
                continue

            is_youth = any(value in normalized_name for value in ("child", "youth", "sr"))
            is_adult = "adult" in normalized_name
            if "package" in section and (is_youth or is_adult):
                age_group = "youth" if is_youth else "adults"
                if "snowboard" in section:
                    result["snowboard"][age_group] = price
                elif "skis" in section or "ski" in section:
                    result["ski"][age_group] = price
                continue

            if "individual items" not in section:
                continue
            if any(age in normalized_name for age in ("child", "youth", "sr")):
                continue
            if "boots" in normalized_name:
                result["items"]["boots"] = price
            elif "snowboard" in normalized_name:
                result["items"]["snowboard"] = price
            elif "ski" in normalized_name:
                result["items"]["skis"] = price
            elif "helmet" in normalized_name:
                result["items"]["helmet"] = price
            elif "pole" in normalized_name:
                result["items"]["poles"] = price

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
