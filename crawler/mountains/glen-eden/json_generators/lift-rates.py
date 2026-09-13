"""Glen Eden lift rates crawler."""

import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

RESORT_ID = "glen-eden"
SOURCE_URL = "https://gleneden.on.ca/plan-your-visit/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}
RATE_KEYS = ("day-week", "day-weekend")
AGE_GROUPS = ("youth", "adults", "seniors")


def is_price(text):
    return bool(re.search(r"\$\d", text))


def fetch_page(url):
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.text


def parse_lift_rates(html):
    result = {"lift_tickets": []}
    soup = BeautifulSoup(html, "html.parser")
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if not rows:
            continue
        headers = [
            cell.get_text(" ", strip=True).lower()
            for cell in rows[0].find_all(["th", "td"])
        ]
        header_text = " ".join(headers)
        is_lift_ticket_table = (
            ("peak" in header_text and "off" in header_text)
            or (
                "age" in header_text
                and any(
                    is_price(cell.get_text())
                    for row in rows[1:]
                    for cell in row.find_all(["td", "th"])
                )
            )
        )
        if not is_lift_ticket_table:
            continue
        for row in rows[1:]:
            cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["td", "th"])]
            if len(cells) < 2 or not cells[0] or not any(is_price(cell) for cell in cells):
                continue
            item = {"category": cells[0], "age_range": cells[1]}
            if len(cells) >= 6:
                item.update(
                    {
                        "peak_online": cells[2],
                        "peak_gate": cells[3],
                        "off_peak_online": cells[4],
                        "off_peak_gate": cells[5],
                    }
                )
            elif len(cells) >= 4:
                item.update({"peak_online": cells[2], "off_peak_online": cells[3]})
            elif len(cells) >= 3:
                item["peak_online"] = cells[2]
            result["lift_tickets"].append(item)
    return result


def parse_price(value):
    if value in (None, ""):
        return None
    match = re.search(r"\$?\s*(\d+(?:[.,]\d+)?)", str(value))
    if not match:
        return None
    amount = float(match.group(1).replace(",", "."))
    return f"${int(amount) if amount.is_integer() else amount:g}"


def get_age_group(category):
    normalized = category.lower()
    if "junior" in normalized or "teen" in normalized or "youth" in normalized:
        return "youth"
    if "adult" in normalized:
        return "adults"
    if "senior" in normalized:
        return "seniors"
    return None


def normalize_lift_rates(rates):
    normalized = {rate_key: {} for rate_key in RATE_KEYS}
    for row in rates.get("lift_tickets", []):
        age_group = get_age_group(row.get("category", ""))
        if age_group not in AGE_GROUPS:
            continue
        off_peak = parse_price(row.get("off_peak_online"))
        peak = parse_price(row.get("peak_online"))
        if off_peak is not None:
            normalized["day-week"][age_group] = off_peak
        if peak is not None:
            normalized["day-weekend"][age_group] = peak

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


def get_lift_rates(url=SOURCE_URL):
    return parse_lift_rates(fetch_page(url))


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
