"""Chicopee lift rates crawler."""

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

URL = "https://www.discoverchicopee.com/plan-a-day"
RESORT_ID = "chicopee"
RATE_KEYS = ("night-week", "night-weekend", "day-week", "day-weekend")
AGE_GROUPS = ("youth", "adults", "seniors")


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
    if not headers:
        first_row = table.find("tr")
        if first_row:
            headers = [
                cell.get_text(separator=" ", strip=True)
                for cell in first_row.find_all(["th", "td"])
            ]

    tbody = table.find("tbody")
    row_elements = tbody.find_all("tr") if tbody else table.find_all("tr")[1:]
    rows = []
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


def get_ticket_name(row):
    return " ".join(str(value) for value in row.values()).lower()


def get_period_value(row, period):
    for label, value in row.items():
        normalized_label = re.sub(r"[^a-z]+", " ", label.lower()).strip()
        if period in normalized_label:
            parsed = parse_price(value)
            if parsed is not None:
                return parsed
    return None


def normalize_lift_rates(rates):
    normalized = {rate_key: {} for rate_key in RATE_KEYS}
    rows = [row for section_rows in rates.values() for row in section_rows]

    for row in rows:
        ticket_name = get_ticket_name(row)
        if "surface lifts" in ticket_name or "tot" in ticket_name:
            continue
        if "all lifts" in ticket_name:
            day_week = get_period_value(row, "weekday")
            day_weekend = get_period_value(row, "weekend")
            if day_week is not None:
                normalized["day-week"] = {
                    age_group: day_week for age_group in AGE_GROUPS
                }
            if day_weekend is not None:
                normalized["day-weekend"] = {
                    age_group: day_weekend for age_group in AGE_GROUPS
                }
        elif "night" in ticket_name:
            night_week = get_period_value(row, "weekday")
            night_weekend = get_period_value(row, "weekend")
            if night_week is not None:
                normalized["night-week"] = {
                    age_group: night_week for age_group in AGE_GROUPS
                }
            if night_weekend is not None:
                normalized["night-weekend"] = {
                    age_group: night_weekend for age_group in AGE_GROUPS
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


def get_rates():
    print(f"Fetching {URL}...")
    driver = get_driver()
    result = {}
    try:
        driver.get(URL)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")
        for section in soup.find_all(["section", "div"]):
            heading = section.find(["h2", "h3"])
            if not heading or "rental" in heading.get_text(" ", strip=True).lower():
                continue
            section_title = heading.get_text(" ", strip=True)
            tables = section.find_all("table", recursive=False) or section.find_all("table")
            rows = [row for table in tables for row in extract_table_data(table)]
            if rows and section_title not in result:
                result[section_title] = rows

        if not result:
            for index, table in enumerate(soup.find_all("table"), 1):
                rows = extract_table_data(table)
                if rows:
                    result[f"Table_{index}"] = rows
    finally:
        driver.quit()
    return result


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
