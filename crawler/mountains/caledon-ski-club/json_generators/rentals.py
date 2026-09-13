"""Caledon Ski Club rental rates crawler."""

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

URL = "https://caledonskiclub.com/proshop"
RESORT_ID = "caledon-ski-club"


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
            header_cells = first_row.find_all(["th", "td"])
            if header_cells and all(cell.name == "th" for cell in header_cells):
                headers = [cell.get_text(separator=" ", strip=True) for cell in header_cells]

    tbody = table.find("tbody")
    row_elements = (
        tbody.find_all("tr")
        if tbody
        else table.find_all("tr")[1:] if headers else table.find_all("tr")
    )
    rows = []
    for row_element in row_elements:
        values = [
            cell.get_text(separator=" ", strip=True)
            for cell in row_element.find_all(["td", "th"])
        ]
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


def extract_price_sections(soup):
    result = {}
    headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    for heading in headings:
        section_title = heading.get_text(" ", strip=True)
        if not section_title:
            continue
        items = []
        sibling = heading.find_next_sibling()
        while sibling and sibling.name not in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            if hasattr(sibling, "find_all"):
                for table in sibling.find_all("table"):
                    items.extend(extract_table_data(table))
            sibling = sibling.find_next_sibling()
        if items:
            result[section_title] = items
    return result


def get_rates():
    print(f"Fetching {URL}...")
    driver = get_driver()
    try:
        driver.get(URL)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")
        result = {}
        for index, table in enumerate(soup.find_all("table")):
            table_data = extract_table_data(table)
            if not table_data:
                continue
            first_row = table_data[0]
            first_key = next(iter(first_row), None) if isinstance(first_row, dict) else None
            section_name = (
                first_key
                if first_key and first_key != "Column_1"
                else f"Rental_Rates_{index + 1}"
            )
            result[section_name] = table_data
        return result or extract_price_sections(soup)
    finally:
        driver.quit()


def parse_price(value):
    if value in (None, ""):
        return None
    match = re.search(r"\$?\s*(\d+(?:[.,]\d+)?)", str(value))
    if not match:
        return None
    amount = float(match.group(1).replace(",", "."))
    return f"${int(amount) if amount.is_integer() else amount:g}"


def get_row_name(row):
    name_key = next(
        (
            key
            for key in row
            if key.lower() in {"name", "item", "category"}
            or "rental" in key.lower()
        ),
        next(iter(row), "name"),
    )
    return str(row.get(name_key, "")), name_key


def get_full_day_price(row, name_key):
    for label, value in row.items():
        if "full day" in label.lower():
            return parse_price(value)
    for label, value in row.items():
        if label != name_key:
            parsed = parse_price(value)
            if parsed is not None:
                return parsed
    return None


def normalize_rentals(rates):
    result = {
        "ski": {},
        "snowboard": {},
        "items": {
            "boots": "$",
            "ice skate": "$",
            "skis": "$",
            "snowboard": "$",
            "poles": "$",
            "helmet": "$",
        },
    }
    for section_name, rows in rates.items():
        section = section_name.lower()
        for row in rows:
            name, name_key = get_row_name(row)
            normalized_name = name.lower()
            price = get_full_day_price(row, name_key)
            if price is None:
                continue

            if "package" in section or "packages" in section:
                if normalized_name == "junior":
                    result["ski"]["youth"] = price
                    result["snowboard"]["youth"] = price
                elif normalized_name == "adult":
                    result["ski"]["adults"] = price
                    result["snowboard"]["adults"] = price
                continue

            if "boot" in normalized_name:
                result["items"]["boots"] = price
            elif "ice skate" in normalized_name or "skate" in normalized_name:
                result["items"]["ice skate"] = price
            elif "ski" in normalized_name and "snowboard" in normalized_name:
                result["items"]["skis"] = price
                result["items"]["snowboard"] = price
            elif "ski" in normalized_name:
                result["items"]["skis"] = price
            elif "snowboard" in normalized_name:
                result["items"]["snowboard"] = price
            elif "pole" in normalized_name and "helmet" in normalized_name:
                result["items"]["poles"] = price
                result["items"]["helmet"] = price
            elif "pole" in normalized_name:
                result["items"]["poles"] = price
            elif "helmet" in normalized_name:
                result["items"]["helmet"] = price

    missing = [
        f"{section}.{age_group}"
        for section in ("ski", "snowboard")
        for age_group in ("youth", "adults")
        if age_group not in result[section]
    ]
    if missing:
        print(f"Missing rental values: {', '.join(missing)}")
        return None
    return result


def main():
    rentals = normalize_rentals(get_rates())
    if rentals is None:
        return
    payload = {
        "rentals": rentals,
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
