import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

URL = "https://brimacombe.ca/plan-your-visit/lift-tickets/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}
RESORT_ID = "brimacombe"
AGE_GROUPS = ("youth", "adults", "seniors")
RATE_KEYS = ("night-week", "night-weekend", "day-week", "day-weekend")


def extract_table_data(table):
    headers = []
    thead = table.find("thead")
    if thead:
        headers = [
            cell.get_text(separator=" ", strip=True)
            for cell in thead.find_all(["th", "td"])
        ]

    rows = []
    tbody = table.find("tbody")
    row_elements = tbody.find_all("tr") if tbody else table.find_all("tr")[1:]
    for row_element in row_elements:
        cells = row_element.find_all(["td", "th"])
        if not cells:
            continue
        values = [cell.get_text(separator=" ", strip=True) for cell in cells]
        if not any(values):
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


def parse_price(value):
    if value in (None, ""):
        return None
    match = re.search(r"\$?\s*(\d+(?:[.,]\d+)?)", str(value))
    if not match:
        return None
    amount = float(match.group(1).replace(",", "."))
    return f"${int(amount) if amount.is_integer() else amount:g}"


def get_age_group(row):
    for value in row.values():
        text = str(value).lower()
        if "13 & under" in text or "youth" in text:
            return "youth"
        if "adult" in text:
            return "adults"
        if "senior" in text:
            return "seniors"
    return None


def get_period_value(row, period):
    for label, value in row.items():
        normalized_label = re.sub(r"[^a-z]+", " ", label.lower()).strip()
        if period in normalized_label or (
            period == "weekend" and "friday to sunday" in normalized_label
        ):
            parsed = parse_price(value)
            if parsed is not None:
                return parsed
    return None


def normalize_lift_rates(rows):
    normalized = {rate_key: {} for rate_key in RATE_KEYS}

    for row in rows:
        age_group = get_age_group(row)
        if age_group not in AGE_GROUPS:
            continue

        weekday_value = get_period_value(row, "monday to thursday")
        if weekday_value is None:
            weekday_value = get_period_value(row, "weekday")

        weekend_value = get_period_value(row, "friday to sunday")
        if weekend_value is None:
            weekend_value = get_period_value(row, "weekend")

        late_night_value = get_period_value(row, "late night")
        if late_night_value is None:
            late_night_value = get_period_value(row, "later night")

        if weekday_value is not None:
            normalized["day-week"][age_group] = weekday_value
        if weekend_value is not None:
            normalized["day-weekend"][age_group] = weekend_value
        if late_night_value is not None:
            normalized["night-week"][age_group] = late_night_value
            normalized["night-weekend"][age_group] = late_night_value

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


def get_lift_rates():
    print(f"Fetching {URL}...")
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table")
    if not table:
        print("No lift rates table found; keeping the existing rates snapshot.")
        return None

    return normalize_lift_rates(extract_table_data(table))


def main():
    rates = get_lift_rates()
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
