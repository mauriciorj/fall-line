"""Horseshoe Valley Resort lift-ticket rates crawler."""

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
RATE_KEYS = ("day-week", "day-weekend")
AGE_GROUPS = ("youth", "adults", "seniors")


def parse_price(value):
    if value in (None, ""):
        return None
    match = re.search(r"\$?\s*(\d+(?:[.,]\d+)?)", str(value))
    if not match:
        return None
    amount = float(match.group(1).replace(",", "."))
    return f"${int(amount) if amount.is_integer() else amount:g}"


def get_age_groups(category):
    normalized = category.lower()
    if "adult" in normalized:
        return ("adults",)
    if "jr" in normalized or "sr" in normalized or "youth" in normalized:
        return ("youth", "seniors")
    return ()


def normalize_lift_rates(rows):
    normalized = {rate_key: {} for rate_key in RATE_KEYS}
    for row in rows:
        age_groups = get_age_groups(row.get("category", ""))
        if not age_groups:
            continue

        weekday = parse_price(row.get("midweek_price"))
        weekend = parse_price(row.get("weekend_price"))
        closing_weekend = parse_price(row.get("closing_weekend"))
        weekday = weekday or closing_weekend
        weekend = weekend or closing_weekend

        for age_group in age_groups:
            if weekday is not None:
                normalized["day-week"][age_group] = weekday
            if weekend is not None:
                normalized["day-weekend"][age_group] = weekend

    missing = [
        f"{rate_key}.{age_group}"
        for rate_key in RATE_KEYS
        for age_group in AGE_GROUPS
        if age_group not in normalized[rate_key]
    ]
    if missing:
        print(f"Missing lift-rate values: {', '.join(missing)}")
        return None
    return normalized


def extract_table_data(table):
    headers = []
    thead = table.find("thead")
    if thead:
        headers = [
            cell.get_text(" ", strip=True)
            for cell in thead.find_all(["th", "td"])
        ]
    if not headers:
        first_row = table.find("tr")
        if first_row:
            headers = [
                cell.get_text(" ", strip=True)
                for cell in first_row.find_all(["th", "td"])
            ]

    rows = []
    tbody = table.find("tbody")
    row_elements = tbody.find_all("tr") if tbody else table.find_all("tr")[1:]
    for row_element in row_elements:
        cells = row_element.find_all(["td", "th"])
        values = [cell.get_text(" ", strip=True) for cell in cells]
        if not values or not any(values) or values == headers:
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


def get_lift_rates():
    response = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    rows = []
    for table in soup.find_all("table"):
        heading = table.find_previous(["h3", "h4", "h5"])
        heading_text = heading.get_text(" ", strip=True) if heading else ""
        headers = " ".join(
            cell.get_text(" ", strip=True)
            for cell in table.find_all("th")
        )
        if "rental" in heading_text.lower() or "rental" in headers.lower():
            continue
        rows.extend(extract_table_data(table))
    return rows


def main():
    rates = normalize_lift_rates(get_lift_rates())
    if rates is None:
        return
    payload = {
        "rates": rates,
        "resortId": RESORT_ID,
        "sourceUrl": SOURCE_URL,
        "updatedAt": int(time.time() * 1000),
    }
    output_file = os.path.join(os.path.dirname(__file__), "lift-rates.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
