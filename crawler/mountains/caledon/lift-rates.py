"""
Caledon Ski Club Lift Rates Crawler
Scrapes lift ticket rates from https://caledonskiclub.com/hours-lift-prices
"""

import json
import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from convex_client import push_resort_rates
from dtos import to_rates_dto

URL = "https://caledonskiclub.com/hours-lift-prices"
RESORT_ID = "caledon-ski-club"
RESORT_NAME = "Caledon Ski Club"


def get_driver():
    """Create and return a configured Chrome WebDriver."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    service = Service()
    return webdriver.Chrome(service=service, options=options)


def extract_table_data(table):
    """Extract table data into a list of dictionaries using thead as keys."""
    headers = []
    thead = table.find("thead")
    if thead:
        headers = [
            th.get_text(separator=" ", strip=True)
            for th in thead.find_all(["th", "td"])
        ]
    else:
        # Try first row as header
        first_row = table.find("tr")
        if first_row:
            headers = [
                cell.get_text(separator=" ", strip=True)
                for cell in first_row.find_all(["th", "td"])
            ]

    rows = []
    tbody = table.find("tbody")
    row_elements = tbody.find_all("tr") if tbody else table.find_all("tr")[1:]
    for tr in row_elements:
        cells = tr.find_all(["td", "th"])
        if not cells:
            continue
        values = [cell.get_text(separator=" ", strip=True) for cell in cells]
        if not any(values):
            continue
        if headers:
            row = {}
            for i, val in enumerate(values):
                key = headers[i] if i < len(headers) and headers[i] else f"Column_{i+1}"
                row[key] = val
            rows.append(row)
        else:
            rows.append(values)
    return rows


def get_lift_rates():
    """Fetch and parse lift ticket rates from Caledon Ski Club."""
    print(f"Fetching {URL}...")
    driver = get_driver()
    result = {}

    try:
        driver.get(URL)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Try to find tables first
        tables = soup.find_all("table")
        if tables:
            for i, table in enumerate(tables):
                # Try to find a heading before the table
                heading = None
                prev = table.find_previous(["h1", "h2", "h3", "h4"])
                if prev:
                    heading = prev.get_text(strip=True)
                
                table_data = extract_table_data(table)
                if table_data:
                    key = heading if heading else f"Table_{i+1}"
                    result[key] = table_data

        # Look for pricing in sections if no tables found
        if not result:
            sections = soup.find_all(["section", "div"], class_=lambda x: x and any(
                word in str(x).lower() for word in ["price", "rate", "ticket", "lift"]
            ))
            for section in sections:
                heading = section.find(["h1", "h2", "h3", "h4"])
                section_title = heading.get_text(strip=True) if heading else "Rates"
                
                # Look for list items or paragraphs with prices
                items = section.find_all(["li", "p"])
                section_data = []
                for item in items:
                    text = item.get_text(strip=True)
                    if "$" in text:
                        section_data.append({"description": text})
                
                if section_data:
                    result[section_title] = section_data

        # Fallback: extract any text containing prices
        if not result:
            page_text = soup.get_text(separator="\n")
            lines = [line.strip() for line in page_text.split("\n") if "$" in line]
            if lines:
                result["Rates"] = [{"description": line} for line in lines]

    finally:
        driver.quit()

    return result


def main():
    rates = get_lift_rates()
    output_file = os.path.join(os.path.dirname(__file__), "lift-rates.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(rates, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")

    result = push_resort_rates(
        RESORT_ID,
        RESORT_NAME,
        URL,
        to_rates_dto(rates),
        fetched_at_ms=int(time.time() * 1000),
    )
    if result is not None:
        print("Pushed to Convex:", result)


if __name__ == "__main__":
    main()
