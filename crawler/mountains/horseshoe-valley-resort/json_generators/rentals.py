"""Horseshoe Valley Resort rental rates crawler."""

import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

RESORT_ID = "horseshoe-valley-resort"
SOURCE_URL = "https://horseshoeresort.com/ski/lift-ticket-and-rentals-pricing/"
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


def get_rentals():
    response = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    result = {}
    for index, table in enumerate(soup.find_all("table"), 1):
        heading = table.find_previous(["h3", "h4", "h5"])
        heading_text = heading.get_text(" ", strip=True) if heading else ""
        rows = table.find_all("tr")
        if not rows:
            continue
        headers = [cell.get_text(" ", strip=True) for cell in rows[0].find_all(["th", "td"])]
        header_text = " ".join(headers)
        if "rental" not in heading_text.lower() and "rental" not in header_text.lower():
            continue
        section = result.setdefault(heading_text or f"rental_table_{index}", [])
        for row in rows[1:]:
            cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["td", "th"])]
            if len(cells) < 2 or not cells[0] or not any(re.search(r"\$\d+", cell) for cell in cells):
                continue
            item = {"item": re.sub(r"\*.*$", "", cells[0]).strip()}
            if len(cells) >= 4:
                item.update({"age_group": cells[1], "midweek_price": cells[2], "weekend_price": cells[3]})
            elif len(cells) == 3:
                item.update({"age_group": cells[1], "closing_weekend": cells[2]})
            else:
                item["price"] = cells[1]
            section.append(item)
    return result


def normalize_rentals(rentals):
    result = {
        "ski": {},
        "snowboard": {},
        "items": {},
    }
    package_prices = {}

    for rows in rentals.values():
        for row in rows:
            name = row.get("item", "")
            normalized_name = name.lower()
            price = next(
                (
                    parse_price(row.get(field))
                    for field in ("closing_weekend", "weekend_price", "price")
                    if parse_price(row.get(field)) is not None
                ),
                None,
            )
            if price is None:
                continue

            age_group = row.get("age_group", "").lower()
            if "ski" in normalized_name and "snowboard" in normalized_name:
                if "adult" in age_group:
                    package_prices["adults"] = price
                elif "jr" in age_group or "sr" in age_group:
                    package_prices["youth"] = price
                continue

            if "boot" in normalized_name:
                result["items"]["boots"] = price
            elif "ice skate" in normalized_name or "skate" in normalized_name:
                result["items"]["ice-skates"] = price
            elif "pole" in normalized_name:
                result["items"]["poles"] = price
            elif "helmet" in normalized_name:
                result["items"]["helmet"] = price

    if "youth" in package_prices and "adults" in package_prices:
        result["ski"] = dict(package_prices)
        result["snowboard"] = dict(package_prices)
        result["items"]["skis"] = package_prices["adults"]
        result["items"]["snowboard"] = package_prices["adults"]

    missing = [
        f"{section}.{age_group}"
        for section in ("ski", "snowboard")
        for age_group in ("youth", "adults")
        if age_group not in result.get(section, {})
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
        "sourceUrl": SOURCE_URL,
        "updatedAt": int(time.time() * 1000),
    }
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
