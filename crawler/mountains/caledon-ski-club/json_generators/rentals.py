"""
Caledon Ski Club rental rates crawler.
Scrapes rates from https://caledonskiclub.com/proshop.
"""

import json
import os
import re
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
from dtos import to_rentals_dto

URL = "https://caledonskiclub.com/proshop"
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

    if not headers:
        first_row = table.find("tr")
        if first_row:
            header_cells = first_row.find_all(["th", "td"])
            if header_cells and all(cell.name == "th" for cell in header_cells):
                headers = [
                    cell.get_text(separator=" ", strip=True)
                    for cell in header_cells
                ]

    tbody = table.find("tbody")
    row_elements = (
        tbody.find_all("tr")
        if tbody
        else table.find_all("tr")[1:] if headers else table.find_all("tr")
    )
    rows = []
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
                for element in sibling.find_all(["li", "p"]):
                    text = element.get_text(" ", strip=True)
                    if re.search(r"\$\d+", text):
                        items.append({"item": text})
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
                first_key if first_key and first_key != "Column_1" else f"Rental_Rates_{index + 1}"
            )
            result[section_name] = table_data
        return result or extract_price_sections(soup)
    finally:
        driver.quit()


def main():
    payload = {
        "rentals": to_rentals_dto(get_rates()),
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
