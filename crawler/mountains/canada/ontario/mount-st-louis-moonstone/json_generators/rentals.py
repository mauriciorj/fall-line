import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

URL = "https://shop.mountstlouis.com/rentals/kit/"
URL_ITEMS = "https://shop.mountstlouis.com/rentals/items/"
RESORT_ID = "mount-st-louis-moonstone"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}
AGE_GROUPS = {
    "adult": "adults",
    "youth": "youth",
}
REQUIRED_ITEM_KEYS = ("boots", "helmet", "poles", "skis", "snowboard")


def fetch_soup(url):
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser")


def normalize_text(value):
    return " ".join(value.lower().split())


def parse_price(value):
    match = re.search(r"\$?\s*([0-9]+(?:[.,][0-9]+)?)", str(value))
    if not match:
        return None
    amount = float(match.group(1).replace(",", "."))
    return f"${int(amount) if amount.is_integer() else amount:g}"


def expand_headers(row):
    headers = []
    for cell in row.find_all(["th", "td"]):
        label = normalize_text(cell.get_text(" ", strip=True))
        colspan = int(cell.get("colspan", 1))
        headers.extend([label] * colspan)
    return headers


def get_pricing_table(soup, required_headers):
    for table in soup.select("table.table-pricing"):
        text = normalize_text(table.get_text(" ", strip=True))
        if all(header in text for header in required_headers):
            return table
    raise ValueError(f"Could not find rental table containing: {required_headers}")


def parse_package_table(table):
    header = table.find("thead")
    header_rows = header.find_all("tr") if header else []
    if len(header_rows) < 2:
        raise ValueError("Rental kit table is missing its headers")

    group_headers = expand_headers(header_rows[0])
    period_headers = expand_headers(header_rows[1])
    if len(group_headers) != len(period_headers):
        raise ValueError("Rental kit table headers have inconsistent columns")

    columns = {
        (group, period): index
        for index, (group, period) in enumerate(zip(group_headers, period_headers))
        if group and period
    }
    required_columns = {
        (category, "day/night")
        for category in ("ski", "snowboard")
    }
    missing_columns = required_columns - columns.keys()
    if missing_columns:
        raise ValueError(f"Missing rental kit columns: {sorted(missing_columns)}")

    rows = table.select("tbody tr") or table.find_all("tr")[len(header_rows):]
    result = {"ski": {}, "snowboard": {}}
    for row in rows:
        cells = row.find_all(["td", "th"])
        if len(cells) < len(period_headers):
            continue

        name = normalize_text(cells[0].get_text(" ", strip=True))
        age_group = next(
            (target for source, target in AGE_GROUPS.items() if source in name),
            None,
        )
        if not age_group:
            continue

        for category in ("ski", "snowboard"):
            price = parse_price(
                cells[columns[(category, "day/night")]].get_text(" ", strip=True)
            )
            if price is None:
                raise ValueError(f"Missing {category} Day/Night price for {name}")
            result[category][age_group] = price

    return result


def parse_item_tables(soup):
    items = {}
    for table in soup.select("table.table-pricing"):
        for row in table.select("tbody tr") or table.find_all("tr")[1:]:
            cells = row.find_all(["td", "th"])
            if len(cells) < 2:
                continue

            name = normalize_text(cells[0].get_text(" ", strip=True))
            price = parse_price(cells[-1].get_text(" ", strip=True))
            if price is None:
                continue

            if "boot" in name:
                items["boots"] = price
            elif "helmet" in name:
                items["helmet"] = price
            elif "pole" in name:
                items["poles"] = price
            elif "ski" in name:
                items["skis"] = price
            elif "snowboard" in name:
                items["snowboard"] = price

    return items


def get_rentals():
    kit_soup = fetch_soup(URL)
    items_soup = fetch_soup(URL_ITEMS)
    kit_table = get_pricing_table(kit_soup, ("ski", "snowboard", "day/night"))
    return {
        "packages": parse_package_table(kit_table),
        "items": parse_item_tables(items_soup),
    }


def normalize_rentals(rentals):
    result = {
        "ski": dict(rentals["packages"]["ski"]),
        "snowboard": dict(rentals["packages"]["snowboard"]),
        "items": dict(rentals["items"]),
    }
    missing = [
        f"{section}.{age_group}"
        for section in ("ski", "snowboard")
        for age_group in ("youth", "adults")
        if age_group not in result[section]
    ]
    missing.extend(
        f"items.{item_key}"
        for item_key in REQUIRED_ITEM_KEYS
        if item_key not in result["items"]
    )
    if missing:
        raise ValueError(f"Missing rental values: {', '.join(missing)}")
    return result


def main():
    payload = {
        "rentals": normalize_rentals(get_rentals()),
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

