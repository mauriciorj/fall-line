"""
Caledon Ski Club Pro Shop Rates Crawler
Scrapes rates from https://caledonskiclub.com/proshop
"""

import json
import re
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
from convex_client import push_resort_rentals
from dtos import to_rentals_dto

URL = "https://caledonskiclub.com/proshop"
RESORT_ID = "caledon-ski-club"


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
    
    # If no thead, try first row as headers
    if not headers:
        first_row = table.find("tr")
        if first_row:
            header_cells = first_row.find_all(["th", "td"])
            if header_cells and all(cell.name == "th" for cell in header_cells):
                headers = [cell.get_text(separator=" ", strip=True) for cell in header_cells]

    rows = []
    tbody = table.find("tbody")
    if tbody:
        row_elements = tbody.find_all("tr")
    else:
        all_rows = table.find_all("tr")
        row_elements = all_rows[1:] if headers else all_rows

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


def extract_price_sections(soup):
    """Extract pricing information from div/section elements."""
    result = {}
    
    # Look for sections with headings followed by price info
    headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    
    for heading in headings:
        section_title = heading.get_text(strip=True)
        if not section_title:
            continue
            
        # Find the next sibling elements until the next heading
        items = []
        sibling = heading.find_next_sibling()
        while sibling and sibling.name not in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            # Check for tables
            tables = sibling.find_all("table") if hasattr(sibling, 'find_all') else []
            for table in tables:
                table_data = extract_table_data(table)
                if table_data:
                    items.extend(table_data)
            
            # Check for list items with prices
            if hasattr(sibling, 'find_all'):
                list_items = sibling.find_all("li")
                for li in list_items:
                    text = li.get_text(strip=True)
                    if re.search(r'\$\d+', text):
                        items.append({"item": text})
                
                # Check for price patterns in paragraphs
                paragraphs = sibling.find_all("p")
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if re.search(r'\$\d+', text):
                        items.append({"item": text})
            
            sibling = sibling.find_next_sibling()
        
        if items:
            result[section_title] = items
    
    return result


def get_rates():
    """Fetch and parse all rates from Caledon Ski Club Pro Shop."""
    print(f"Fetching {URL}...")
    driver = get_driver()
    result = {}

    try:
        driver.get(URL)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # First, try to extract tables
        tables = soup.find_all("table")
        for i, table in enumerate(tables):
            table_data = extract_table_data(table)
            if table_data:
                # Use first column header as section name if available
                first_row = table_data[0] if table_data else {}
                first_key = list(first_row.keys())[0] if isinstance(first_row, dict) and first_row else None
                section_name = first_key if first_key and first_key not in ["Column_1"] else f"Rental_Rates_{i+1}"
                
                if section_name in result:
                    result[section_name].extend(table_data)
                else:
                    result[section_name] = table_data

        # If no tables found, try extracting from sections
        if not result:
            result = extract_price_sections(soup)

        # Look for any pricing divs or cards
        if not result:
            price_containers = soup.find_all(["div", "article", "section"], 
                                              class_=re.compile(r'price|rate|product|item|card', re.I))
            for container in price_containers:
                title_elem = container.find(["h1", "h2", "h3", "h4", "h5", "h6", "strong", "b"])
                title = title_elem.get_text(strip=True) if title_elem else "Unknown"
                
                price_match = re.search(r'\$[\d,.]+', container.get_text())
                if price_match:
                    if "Products" not in result:
                        result["Products"] = []
                    result["Products"].append({
                        "name": title,
                        "price": price_match.group()
                    })

    finally:
        driver.quit()

    return result


def main():
    rates = get_rates()
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(rates, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")

    result = push_resort_rentals(
        RESORT_ID,
        URL,
        to_rentals_dto(rates),
        updated_at_ms=int(time.time() * 1000),
    )
    if result is not None:
        print("Pushed to Convex:", result)


if __name__ == "__main__":
    main()
