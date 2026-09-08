"""
Caledon Ski Club lift rates crawler.
Scrapes the lift ticket table from https://caledonskiclub.com/hours-lift-prices.
"""

import json
import os
import sys
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dtos import to_rates_dto

URL = "https://caledonskiclub.com/hours-lift-prices"
RESORT_ID = "caledon-ski-club"


def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
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
        if headers:
            rows.append(
                {
                    headers[index] if index < len(headers) and headers[index] else f"Column_{index + 1}": value
                    for index, value in enumerate(values)
                }
            )
        else:
            rows.append(values)
    return rows


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
        return extract_table_data(table) if table else []
    finally:
        driver.quit()


def main():
    payload = {
        "rates": to_rates_dto(get_lift_rates()),
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
