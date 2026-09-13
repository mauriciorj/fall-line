"""Caledon Ski Club lift-rate crawler."""

import json
import os
import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL = "https://caledonskiclub.com/hours-lift-prices"
RESORT_ID = "caledon-ski-club"
AGE_GROUPS = ("youth", "adults", "seniors")
RATE_KEYS = ("day-week", "day-weekend")


def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(service=Service(), options=options)


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
    tbody = table.find("tbody")
    row_elements = tbody.find_all("tr") if tbody else table.find_all("tr")[1:]
    for row_element in row_elements:
        cells = row_element.find_all(["td", "th"])
        values = [cell.get_text(separator=" ", strip=True) for cell in cells]
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
        if "child 6" in text or "youth" in text:
            return "youth"
        if "adult" in text:
            return "adults"
        if "senior" in text:
            return "seniors"
    return None


def get_period_value(row, period):
    for label, value in row.items():
        normalized_label = re.sub(r"[^a-z]+", " ", label.lower()).strip()
        if period in normalized_label:
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

        weekday_value = get_period_value(row, "mid week full day")
        if weekday_value is None:
            weekday_value = get_period_value(row, "midweek full day")
        weekend_value = get_period_value(row, "weekends holidays")
        if weekend_value is None:
            weekend_value = get_period_value(row, "weekend")

        if weekday_value is not None:
            normalized["day-week"][age_group] = weekday_value
        if weekend_value is not None:
            normalized["day-weekend"][age_group] = weekend_value

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
    driver = get_driver()
    try:
        driver.get(URL)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")
        table = soup.find("table")
        if not table:
            print("No lift rates table found; keeping the existing rates snapshot.")
            return None
        return normalize_lift_rates(extract_table_data(table))
    finally:
        driver.quit()


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
