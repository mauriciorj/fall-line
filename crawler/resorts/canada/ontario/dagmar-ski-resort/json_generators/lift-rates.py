"""Dagmar lift-ticket rates crawler."""

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
RATE_KEYS = ("night-week", "night-weekend", "day-week", "day-weekend")
AGE_GROUPS = ("youth", "adults", "seniors")
TABLE_SECTIONS = {
    0: "8 Pack Value-Priced Lift Tickets",
    1: "Anytime Alpine Lift Tickets",
    2: "Special Late-Night After 6 and Last Call",
    3: "Magic Carpet Special for Beginners",
    4: "Seniors 60+",
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


def parse_price(value):
    if value in (None, ""):
        return None
    match = re.search(r"\$?\s*(\d+(?:[.,]\d+)?)", str(value))
    if not match:
        return None
    amount = float(match.group(1).replace(",", "."))
    return f"${int(amount) if amount.is_integer() else amount:g}"


def row_text(section_name, row):
    return " ".join([section_name, *[str(value) for value in row.values()]]).lower()


def row_prices(row):
    for label, value in row.items():
        normalized_label = label.lower()
        if "ticket" in normalized_label or normalized_label in {
            "name",
            "category",
            "column_1",
        }:
            continue
        parsed = parse_price(value)
        if parsed is not None:
            yield normalized_label, parsed


def add_day_rates(normalized, section_name, row):
    text = row_text(section_name, row)
    if "anytime alpine" not in text or "full day" not in text:
        return

    for label, value in row_prices(row):
        if "adult" in label:
            for rate_key in ("day-week", "day-weekend"):
                normalized[rate_key]["youth"] = value
                normalized[rate_key]["adults"] = value
        elif "sr" in label or "senior" in label or "60+" in label:
            normalized["day-week"]["seniors"] = value
            normalized["day-weekend"]["seniors"] = value
        elif "jr" in label or "junior" in label or "6-17" in label:
            normalized["day-week"]["youth"] = value
            normalized["day-weekend"]["youth"] = value


def add_night_rates(normalized, section_name, row):
    text = row_text(section_name, row)
    if "special late-night" not in text:
        return
    if "after 6" not in text and "last call" not in text:
        return

    value = next((value for _, value in row_prices(row)), None)
    if value is None:
        return
    for rate_key in ("night-week", "night-weekend"):
        for age_group in AGE_GROUPS:
            normalized[rate_key][age_group] = value


def normalize_lift_rates(rates):
    normalized = {rate_key: {} for rate_key in RATE_KEYS}
    for section_name, rows in rates.items():
        for row in rows:
            add_day_rates(normalized, section_name, row)
            add_night_rates(normalized, section_name, row)

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


def get_rates():
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    tables = BeautifulSoup(response.content, "html.parser").find_all("table", class_="table")
    return {
        section: rows
        for index, table in enumerate(tables)
        if (section := TABLE_SECTIONS.get(index)) and (rows := extract_table_data(table))
    }


def main():
    rates = normalize_lift_rates(get_rates())
    if rates is None:
        return
    payload = {
        "rates": rates,
        "resortId": RESORT_ID,
        "sourceUrl": URL,
        "updatedAt": int(time.time() * 1000),
    }
    output_file = os.path.join(os.path.dirname(__file__), "lift-rates.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
