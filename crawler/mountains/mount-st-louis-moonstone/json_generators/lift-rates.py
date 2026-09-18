import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

RESORT_ID = "mount-st-louis-moonstone"
DAY_URL = "https://shop.mountstlouis.com/lift-tickets/day/"
NIGHT_URL = "https://shop.mountstlouis.com/lift-tickets/night/"
AGE_GROUPS = {
    "adult 18+": "adults",
    "youth 6-17": "youth",
    "senior 65+": "seniors",
}
RATE_KEYS = ("day-week", "day-weekend", "night-week", "night-weekend")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}


def fetch_soup(url):
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser")


def normalize_text(value):
    return " ".join(value.lower().split())


def parse_price(value):
    match = re.search(r"\$\s*([0-9]+(?:[.,][0-9]+)?)", value)
    if not match:
        return None
    amount = float(match.group(1).replace(",", "."))
    return f"${int(amount) if amount.is_integer() else amount:g}"


def get_table_context(table):
    headings = table.find_all_previous(["h1", "h2", "h3", "h4", "h5", "h6"], limit=3)
    return " ".join(normalize_text(heading.get_text(" ", strip=True)) for heading in headings)


def get_period(table, time_of_day):
    context = get_table_context(table)
    if time_of_day == "day" and re.search(r"day\s*\(\s*9:00am\s*-\s*4:00pm\s*\)", context):
        return "day"
    if time_of_day == "night" and re.search(r"night\s*\(\s*4:00\s*-\s*9:00pm\s*\)", context):
        return "night"
    return None


def get_buy_now_column(table):
    header = table.find("thead")
    if not header:
        return None

    headers = [normalize_text(cell.get_text(" ", strip=True)) for cell in header.find_all(["th", "td"])]
    for index, value in enumerate(headers):
        if "buy now" in value and "save" in value:
            return index
    return None


def parse_table(table):
    buy_now_index = get_buy_now_column(table)
    if buy_now_index is None:
        return {}

    rates = {}
    tbody = table.find("tbody")
    rows = tbody.find_all("tr") if tbody else table.find_all("tr")[1:]
    for row in rows:
        cells = row.find_all(["td", "th"])
        if len(cells) <= buy_now_index:
            continue

        age_group = normalize_text(cells[0].get_text(" ", strip=True)).rstrip("*")
        age_group = AGE_GROUPS.get(age_group)
        if not age_group:
            continue

        price = parse_price(cells[buy_now_index].get_text(" ", strip=True))
        if price:
            rates[age_group] = price
    return rates


def parse_period(soup, time_of_day):
    for table in soup.find_all("table"):
        if get_period(table, time_of_day) != time_of_day:
            continue
        rates = parse_table(table)
        if rates:
            missing = set(AGE_GROUPS.values()) - rates.keys()
            if missing:
                raise ValueError(f"Missing {time_of_day} rates: {sorted(missing)}")
            return rates
    raise ValueError(f"Could not find {time_of_day} lift-rate table")


def get_lift_rates():
    day_rates = parse_period(fetch_soup(DAY_URL), "day")
    night_rates = parse_period(fetch_soup(NIGHT_URL), "night")
    return {
        "day-week": dict(day_rates),
        "day-weekend": dict(day_rates),
        "night-week": dict(night_rates),
        "night-weekend": dict(night_rates),
    }


def main():
    payload = {
        "rates": get_lift_rates(),
        "resortId": RESORT_ID,
        "sourceUrl": DAY_URL,
        "updatedAt": int(time.time() * 1000),
    }
    output_file = os.path.join(os.path.dirname(__file__), "lift-rates.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
