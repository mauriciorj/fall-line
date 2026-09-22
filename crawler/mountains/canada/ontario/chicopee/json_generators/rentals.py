"""Chicopee rental rates crawler."""

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


def get_rentals():
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
            if not heading or "rental" not in heading.get_text(" ", strip=True).lower():
                continue
            section_title = heading.get_text(" ", strip=True)
            tables = section.find_all("table", recursive=False) or section.find_all("table")
            rows = [row for table in tables for row in extract_table_data(table)]
            if rows and section_title not in result:
                result[section_title] = rows
    finally:
        driver.quit()
    return result


def parse_price(value):
    if value in (None, ""):
        return None
    match = re.search(r"\$?\s*(\d+(?:[.,]\d+)?)", str(value))
    if not match:
        return None
    amount = float(match.group(1).replace(",", "."))
    return f"${int(amount) if amount.is_integer() else amount:g}"


def normalize_rentals(rentals):
    result = {"ski": {}, "snowboard": {}}
    for rows in rentals.values():
        for row in rows:
            name = " ".join(str(value) for value in row.values()).lower()
            weekend_price = next(
                (
                    parse_price(value)
                    for label, value in row.items()
                    if "weekend" in label.lower() and parse_price(value) is not None
                ),
                None,
            )
            if weekend_price is None:
                continue
            if "tot" in name and "ski/board" in name:
                result["ski"]["youth"] = weekend_price
                result["snowboard"]["youth"] = weekend_price
            elif "ski/board" in name:
                result["ski"]["adults"] = weekend_price
                result["snowboard"]["adults"] = weekend_price

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
    rentals = normalize_rentals(get_rentals())
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
