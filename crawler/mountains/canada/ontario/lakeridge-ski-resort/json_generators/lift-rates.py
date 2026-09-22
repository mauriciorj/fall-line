"""Lakeridge lift-ticket rates crawler."""

import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

URL = "https://ski-lakeridge.com/skiing-snowboarding/hours-ticket-prices/"
RESORT_ID = "lakeridge-ski-resort"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}
RATE_KEYS = ("night-week", "night-weekend", "day-week", "day-weekend")
AGE_GROUPS = ("youth", "adults", "seniors")


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


def parse_price(value):
    if value in (None, ""):
        return None
    match = re.search(r"\$?\s*(\d+(?:[.,]\d+)?)", str(value))
    if not match:
        return None
    raw_amount = match.group(1).replace(",", ".")
    amount = float(raw_amount)
    if "." in raw_amount:
        return f"${amount:.2f}"
    return f"${int(amount)}"


def get_numeric_values(row):
    return [
        parsed
        for value in row.values()
        if (parsed := parse_price(value)) is not None
    ]


def normalize_lift_rates(rates):
    normalized = {rate_key: {} for rate_key in RATE_KEYS}
    for section_name, rows in rates.items():
        section = section_name.lower()
        if "monday to wednesday" in section:
            day_prefix = "week"
        elif "thursday to sunday" in section:
            day_prefix = "weekend"
        else:
            continue

        for row in rows:
            row_text = " ".join([*row.keys(), *[str(value) for value in row.values()]]).lower()
            if "online pricing" not in row_text:
                continue
            if "4 hours anytime" in row_text:
                rate_key = f"day-{day_prefix}"
            elif "3 hours" in row_text and "6:30pm" in row_text:
                rate_key = f"night-{day_prefix}"
            else:
                continue

            prices = get_numeric_values(row)
            if len(prices) < 2:
                continue
            adults = prices[0]
            youth_and_seniors = prices[1]
            normalized[rate_key] = {
                "youth": youth_and_seniors,
                "adults": adults,
                "seniors": youth_and_seniors,
            }

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
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    result = {}
    for title in [
        "Beginner Area Ticket Prices",
        "Monday to Wednesday Lift Tickets",
        "Thursday to Sunday Lift Tickets",
    ]:
        heading = soup.find(
            "h2", string=lambda text: text and title.lower() in text.lower()
        )
        if heading:
            table = heading.find_next("table")
            rows = extract_table_data(table) if table else []
            if rows:
                result[title] = rows
    return result


def main():
    rates = normalize_lift_rates(get_lift_rates())
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
