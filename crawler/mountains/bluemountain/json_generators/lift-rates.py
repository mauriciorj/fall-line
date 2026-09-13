import json
import os
import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL = "https://www.bluemountain.ca/plan-your-trip/day-tickets/winter-lift-tickets"
RESORT_ID = "blue-mountain"
AGE_GROUPS = ("youth", "adults", "seniors")
RATE_KEYS = ("night-week", "night-weekend", "day-week", "day-weekend")


def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(options=options)


def extract_table_data(table):
    thead = table.find("thead")
    headers = (
        [
            cell.get_text(separator=" ", strip=True)
            for cell in thead.find_all(["th", "td"])
        ]
        if thead
        else []
    )
    rows = []
    row_elements = table.find_all("tr")[1:] if not thead else table.find_all("tr")
    for row_element in row_elements:
        values = [
            cell.get_text(separator=" ", strip=True)
            for cell in row_element.find_all(["td", "th"])
        ]
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


def get_table_context(table):
    parts = []
    caption = table.find("caption")
    if caption:
        parts.append(caption.get_text(" ", strip=True))

    for heading in table.find_all_previous(["h1", "h2", "h3", "h4", "h5", "h6"], limit=6):
        text = heading.get_text(" ", strip=True)
        if text:
            parts.append(text)
        if re.search(r"\b(day|night)\b", text, re.I):
            break

    return " ".join(parts).lower()


def get_age_group(row):
    for value in row.values():
        text = str(value).lower()
        if "youth" in text:
            return "youth"
        if "adult" in text:
            return "adults"
        if "senior" in text:
            return "seniors"
    return None


def get_period_value(row, period):
    for label, value in row.items():
        normalized_label = re.sub(r"[^a-z]+", " ", label.lower()).strip()
        if period in normalized_label and "in season" in normalized_label:
            return parse_price(value)
    return None


def get_fallback_period_value(row, context, period):
    if period not in context:
        return None
    for label, value in row.items():
        if label.lower().startswith("column_") or label.lower() in {
            "age",
            "age category",
            "category",
            "name",
        }:
            continue
        parsed = parse_price(value)
        if parsed:
            return parsed
    return None


def normalize_lift_rates(soup):
    normalized = {rate_key: {} for rate_key in RATE_KEYS}

    for table in soup.find_all("table"):
        rows = extract_table_data(table)
        if not rows:
            continue
        context = get_table_context(table)
        if "night" in context:
            time_of_day = "night"
        elif "day" in context:
            time_of_day = "day"
        else:
            continue

        for row in rows:
            age_group = get_age_group(row)
            if age_group not in AGE_GROUPS:
                continue
            for period, suffix in (("midweek", "week"), ("weekend", "weekend")):
                value = get_period_value(row, period)
                if value is None:
                    value = get_fallback_period_value(row, context, period)
                if value is not None:
                    normalized[f"{time_of_day}-{suffix}"][age_group] = value

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
    driver = get_driver()
    try:
        driver.get(URL)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
        except TimeoutException:
            print("No lift rates table found; keeping the existing rates snapshot.")
            return None
        soup = BeautifulSoup(driver.page_source, "html.parser")
        return normalize_lift_rates(soup)
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
