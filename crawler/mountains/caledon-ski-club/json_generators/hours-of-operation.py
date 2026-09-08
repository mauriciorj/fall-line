"""
Caledon Ski Club hours crawler.
Scrapes hours from https://caledonskiclub.com/hours-lift-prices.
"""

import json
import os
import re
import sys
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dtos import to_hours

URL = "https://caledonskiclub.com/hours-lift-prices"
RESORT_ID = "caledon-ski-club"
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def get_hours():
    print(f"Fetching {URL}...")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(URL)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        return extract_hours(BeautifulSoup(driver.page_source, "html.parser"))
    finally:
        driver.quit()


def extract_hours(soup):
    result = {}
    for table in soup.find_all("table"):
        rows = []
        for row in table.find_all("tr"):
            cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["th", "td"])]
            if cells:
                rows.append(cells)
        if not rows:
            continue

        headers = [cell.lower() for cell in rows[0]]
        day_columns = {
            index: day
            for index, value in enumerate(headers)
            for day in DAYS
            if value.startswith(day.lower())
        }
        if day_columns:
            section_name = _table_section_name(table)
            section = result.setdefault(section_name, {})
            for row in rows[1:]:
                if len(row) <= max(day_columns):
                    continue
                for index, day in day_columns.items():
                    if row[index]:
                        section[day] = row[index]
            continue

        for row in rows:
            if len(row) >= 2:
                day = next((day for day in DAYS if row[0].lower().startswith(day.lower())), None)
                if day:
                    result.setdefault(_table_section_name(table), {})[day] = row[1]

    result = {name: days for name, days in result.items() if days}
    if result:
        return result

    page_text = soup.get_text(" ", strip=True)
    match = re.search(r"Lifts?\s+Operate\s+from\s+(.+?)(?:!|\.)", page_text, re.IGNORECASE)
    if match:
        return {"Lift Operations": {"Daily": match.group(1).strip()}}
    return {}


def _table_section_name(table):
    heading = table.find_previous(["h1", "h2", "h3", "h4", "h5", "h6"])
    return heading.get_text(" ", strip=True) if heading else "Hours of Operation"


def main():
    payload = {
        "hours": to_hours(get_hours()),
        "resortId": RESORT_ID,
        "sourceUrl": URL,
        "updatedAt": int(time.time() * 1000),
    }
    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
