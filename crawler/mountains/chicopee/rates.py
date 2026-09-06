import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

URL = "https://www.discoverchicopee.com/plan-a-day"


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


def get_rates():
    """Fetch and parse lift ticket rates from Chicopee's Plan A Day page."""
    print(f"Fetching {URL}...")
    driver = get_driver()
    result = {}

    try:
        driver.get(URL)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )

        soup = BeautifulSoup(driver.page_source, "html.parser")

        sections = soup.find_all(["section", "div"])
        for section in sections:
            heading = section.find(["h2", "h3"])
            if not heading:
                continue
            section_title = heading.get_text(strip=True)
            
            # Only include lift ticket sections, skip rental sections
            if "rental" in section_title.lower():
                continue

            tables = section.find_all("table", recursive=False)
            if not tables:
                tables = section.find_all("table")

            if tables:
                section_data = []
                for table in tables:
                    table_data = extract_table_data(table)
                    if table_data:
                        section_data.extend(table_data)
                if section_data and section_title not in result:
                    result[section_title] = section_data

        if not result:
            tables = soup.find_all("table")
            for i, table in enumerate(tables):
                table_data = extract_table_data(table)
                if table_data:
                    result[f"Table_{i+1}"] = table_data

    finally:
        driver.quit()

    return result


def main():
    rates = get_rates()
    output_file = os.path.join(os.path.dirname(__file__), "rates.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(rates, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
