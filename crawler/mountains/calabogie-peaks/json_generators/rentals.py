import json
import os
import re
import time
from datetime import date

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

SOURCE_URL = "https://calabogie.com/"
PAGE_URL = "https://calabogie.com/product-category/rentals/"
RESORT_ID = "calabogie-peaks"
PRODUCTS = {
    "ski package": "ski",
    "snowboard package": "snowboard",
    "helmet only": "helmet",
    "poles only": "poles",
    "ski boots only": "boots",
}
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(HEADERS["User-Agent"])
    return webdriver.Chrome(options=options)


def normalize_text(value):
    return " ".join(value.lower().split())


def parse_price(value):
    match = re.search(r"\$\s*([0-9]+(?:[.,][0-9]+)?)", value)
    if not match:
        return None
    amount = float(match.group(1).replace(",", "."))
    return f"${int(amount) if amount.is_integer() else amount:g}"


def collect_product_links(driver):
    driver.get(PAGE_URL)
    links = {}
    for link in driver.find_elements(By.XPATH, "//a[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'buy now')]"):
        href = link.get_attribute("href")
        card = link.find_element(By.XPATH, "ancestor::*[self::article or contains(@class, 'product')][1]")
        name = normalize_text(card.text if card else link.text)
        for product_name, key in PRODUCTS.items():
            if product_name in name and href:
                links[key] = href
    if set(PRODUCTS.values()) - links.keys():
        raise ValueError(f"Missing rental product links: {sorted(set(PRODUCTS.values()) - links.keys())}")
    return links


def set_booking_fields(driver):
    today = date.today().isoformat()
    for element in driver.find_elements(By.CSS_SELECTOR, "input"):
        descriptor = normalize_text(f"{element.get_attribute('name') or ''} {element.get_attribute('placeholder') or ''} {element.get_attribute('aria-label') or ''}")
        if "date" in descriptor:
            driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change', {bubbles: true}));", element, today)
    for element in driver.find_elements(By.TAG_NAME, "select"):
        options = [normalize_text(option.text) for option in Select(element).options]
        if "1 day" in options:
            Select(element).select_by_visible_text("1 Day")
        elif "between 9am and 4pm" in options:
            Select(element).select_by_visible_text("Between 9am and 4pm")


def get_all_ages_price(driver):
    text = " ".join(BeautifulSoup(driver.page_source, "html.parser").get_text(" ", strip=True).split())
    match = re.search(r"all ages.{0,250}?\$\s*([0-9]+(?:[.,][0-9]+)?)", text, re.IGNORECASE)
    if not match:
        match = re.search(r"\$\s*([0-9]+(?:[.,][0-9]+)?)", text)
    if not match:
        raise ValueError("Could not find ALL AGES rental price")
    return parse_price(match.group())


def get_rentals():
    driver = get_driver()
    try:
        links = collect_product_links(driver)
        prices = {}
        for key, url in links.items():
            driver.get(url)
            set_booking_fields(driver)
            prices[key] = get_all_ages_price(driver)
        package_price = {"adults": prices["ski"], "youth": prices["ski"]}
        return {
            "ski": dict(package_price),
            "snowboard": {"adults": prices["snowboard"], "youth": prices["snowboard"]},
            "items": {"helmet": prices["helmet"], "poles": prices["poles"], "boots": prices["boots"]},
        }
    finally:
        driver.quit()


def main():
    payload = {"rentals": get_rentals(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
