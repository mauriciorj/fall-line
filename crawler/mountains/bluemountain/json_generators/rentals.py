import json
import os
import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from dtos import to_rentals_dto

RESORT_ID = "blue-mountain"
URLS = {
    "adult_ski": "https://www.bluemountain.ca/plan-your-trip/rentals/adult-ski",
    "adult_snowboard": "https://www.bluemountain.ca/plan-your-trip/rentals/adult-snowboard",
    "youth_ski": "https://www.bluemountain.ca/plan-your-trip/rentals/youth-ski",
    "youth_snowboard": "https://www.bluemountain.ca/plan-your-trip/rentals/youth-snowboard",
}


def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(options=options)


def select_date_and_wait(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".datepicker__day"))
        )
        valid_dates = driver.find_elements(
            By.CSS_SELECTOR,
            ".datepicker__pane:first-child .datepicker__day:not(.is-disabled):not(.is-otherMonth)",
        )
        if len(valid_dates) <= 5:
            return False
        target = valid_dates[min(7, len(valid_dates) - 1)]
        driver.execute_script("arguments[0].scrollIntoView(true);", target)
        driver.execute_script("arguments[0].click();", target)
        for _ in range(20):
            time.sleep(0.5)
            if "$" in driver.page_source or "Sold Out" in driver.page_source:
                return True
    except Exception as error:
        print(f"Date selection error: {error}")
    return False


def parse_rental_products(soup):
    products = []
    result_items = soup.find_all(class_=lambda value: value and "result-item" in str(value).lower())
    for item in result_items:
        product = {}
        name = item.find(class_=lambda value: value and "name" in str(value).lower())
        price = item.find(class_=lambda value: value and "price" in str(value).lower())
        description = item.find(class_=lambda value: value and "desc" in str(value).lower())
        if name:
            product["name"] = name.get_text(strip=True)
        if price:
            product["price"] = price.get_text(strip=True)
        if description:
            product["description"] = description.get_text(separator=" ", strip=True)
        if product:
            products.append(product)
    return products


def parse_price_cards(soup):
    cards = []
    for element in soup.find_all(string=re.compile(r"\$\d+")):
        parent = element.find_parent(["div", "li", "span", "p"])
        if not parent:
            continue
        text = parent.get_text(separator=" | ", strip=True)
        match = re.search(r"\$[\d,]+(?:\.\d{2})?", text)
        if text and len(text) < 300 and match:
            cards.append({"text": text, "price": match.group()})
    seen = set()
    return [card for card in cards if not (card["text"] in seen or seen.add(card["text"]))]


def get_rental_page(driver, category, url):
    print(f"Fetching {category}: {url}...")
    driver.get(url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    result = {"category": category, "url": url}
    title = soup.find("h1")
    if title:
        result["title"] = title.get_text(strip=True)
    description = soup.find("meta", {"name": "description"})
    if description:
        result["description"] = description.get("content", "")
    if not select_date_and_wait(driver):
        result["note"] = "Dynamic pricing requires date selection on website"
        return result
    soup = BeautifulSoup(driver.page_source, "html.parser")
    products = parse_rental_products(soup)
    pricing = parse_price_cards(soup)
    if products:
        result["products"] = products
    if pricing:
        result["pricing"] = pricing
    return result


def get_rentals():
    driver = get_driver()
    try:
        results = {}
        for category, url in URLS.items():
            try:
                results[category] = get_rental_page(driver, category, url)
            except Exception as error:
                print(f"Error fetching {category}: {error}")
                results[category] = {"error": str(error)}
        return results
    finally:
        driver.quit()


def main():
    payload = {
        "rentals": to_rentals_dto(get_rentals()),
        "resortId": RESORT_ID,
        "sourceUrl": next(iter(URLS.values())),
        "updatedAt": int(time.time() * 1000),
    }
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
