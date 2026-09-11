import json
import os
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

from dtos import to_rates_dto

URL = "https://www.bluemountain.ca/plan-your-trip/day-tickets/winter-lift-tickets"
RESORT_ID = "blue-mountain"


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
    headers = [
        cell.get_text(separator=" ", strip=True)
        for cell in thead.find_all(["th", "td"])
    ] if thead else []
    rows = []
    row_elements = table.find_all("tr")[1:] if not thead else table.find_all("tr")
    for row_element in row_elements:
        values = [cell.get_text(separator=" ", strip=True) for cell in row_element.find_all(["td", "th"])]
        if not any(values):
            continue
        rows.append(
            {
                headers[index] if index < len(headers) and headers[index] else f"Column_{index + 1}": value
                for index, value in enumerate(values)
            }
        )
    return rows


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
        result = {}
        for index, table in enumerate(soup.find_all("table"), start=1):
            rows = extract_table_data(table)
            if rows:
                result[f"Table_{index}"] = rows
        return result
    finally:
        driver.quit()


def main():
    rates = get_lift_rates()
    if rates is None:
        return
    payload = {
        "rates": to_rates_dto(rates),
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
