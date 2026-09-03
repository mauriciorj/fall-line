from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import json
import time
import re
import os

URLS = {
    "adult_ski": "https://www.bluemountain.ca/plan-your-trip/rentals/adult-ski",
    "adult_snowboard": "https://www.bluemountain.ca/plan-your-trip/rentals/adult-snowboard",
    "youth_ski": "https://www.bluemountain.ca/plan-your-trip/rentals/youth-ski",
    "youth_snowboard": "https://www.bluemountain.ca/plan-your-trip/rentals/youth-snowboard",
}


def get_driver():
    """Create and return a headless Chrome driver."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    return webdriver.Chrome(options=options)


def select_date_and_wait(driver):
    """Select a date from the datepicker and wait for prices to load."""
    try:
        # Wait for datepicker to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".datepicker__day"))
        )
        
        # Find valid dates (not disabled, not other month)
        valid_dates = driver.find_elements(
            By.CSS_SELECTOR, 
            ".datepicker__pane:first-child .datepicker__day:not(.is-disabled):not(.is-otherMonth)"
        )
        
        if valid_dates and len(valid_dates) > 5:
            # Click on a date about a week out
            target = valid_dates[min(7, len(valid_dates) - 1)]
            driver.execute_script("arguments[0].scrollIntoView(true);", target)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", target)
            
            # Wait for prices to load (look for dollar sign or "sold out")
            for _ in range(20):
                time.sleep(0.5)
                if "$" in driver.page_source or "Sold Out" in driver.page_source:
                    time.sleep(1)
                    return True
            
        return False
    except Exception as e:
        print(f"Date selection error: {e}")
        return False


def parse_rental_products(soup):
    """Parse rental product information from the page."""
    products = []
    
    # Look for product result items
    result_items = soup.find_all(class_=lambda c: c and "result-item" in str(c).lower())
    
    for item in result_items:
        product = {}
        
        # Get product name
        name_el = item.find(class_=lambda c: c and "name" in str(c).lower())
        if name_el:
            product["name"] = name_el.get_text(strip=True)
        
        # Get price
        price_el = item.find(class_=lambda c: c and "price" in str(c).lower())
        if price_el:
            product["price"] = price_el.get_text(strip=True)
        
        # Get description
        desc_el = item.find(class_=lambda c: c and "desc" in str(c).lower())
        if desc_el:
            product["description"] = desc_el.get_text(separator=" ", strip=True)
        
        if product:
            products.append(product)
    
    # Also look for accordion items or card-based layouts
    accordion_items = soup.find_all(class_=lambda c: c and "accordion" in str(c).lower())
    for item in accordion_items:
        text = item.get_text(separator=" | ", strip=True)
        if "$" in text and len(text) < 500:
            # Extract price info
            price_match = re.search(r"\$[\d,]+(?:\.\d{2})?", text)
            if price_match:
                products.append({
                    "text": text,
                    "price": price_match.group()
                })
    
    return products


def parse_price_cards(soup):
    """Parse price cards from the page."""
    cards = []
    
    # Look for elements containing prices
    for el in soup.find_all(string=re.compile(r"\$\d+")):
        parent = el.find_parent(["div", "li", "span", "p"])
        if parent:
            card_text = parent.get_text(separator=" | ", strip=True)
            if card_text and len(card_text) < 300:
                # Extract structured data
                price_match = re.search(r"\$[\d,]+(?:\.\d{2})?", card_text)
                cards.append({
                    "text": card_text,
                    "price": price_match.group() if price_match else None
                })
    
    # Deduplicate
    seen = set()
    unique_cards = []
    for card in cards:
        key = card.get("text", "")
        if key not in seen:
            seen.add(key)
            unique_cards.append(card)
    
    return unique_cards


def get_page_metadata(soup):
    """Extract metadata about the rental page."""
    metadata = {}
    
    # Get title
    h1 = soup.find("h1")
    if h1:
        metadata["title"] = h1.get_text(strip=True)
    
    # Get description from meta or page content
    meta_desc = soup.find("meta", {"name": "description"})
    if meta_desc:
        metadata["description"] = meta_desc.get("content", "")
    
    # Get Inntopia product IDs if available
    inntopia_id = soup.find(class_="inntopia-id")
    if inntopia_id:
        metadata["inntopia_id"] = inntopia_id.get_text(strip=True)
    
    return metadata


def get_rentals_from_url(driver, url, category):
    """Fetch and parse rental data from a single URL using Selenium."""
    print(f"Fetching {category}: {url}...")
    driver.get(url)
    time.sleep(3)
    
    result = {
        "category": category,
        "url": url,
    }
    
    # Get initial page data
    soup = BeautifulSoup(driver.page_source, "html.parser")
    metadata = get_page_metadata(soup)
    result.update(metadata)
    
    # Try to select a date and load prices
    prices_loaded = select_date_and_wait(driver)
    
    if prices_loaded:
        # Re-parse page after prices loaded
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        products = parse_rental_products(soup)
        if products:
            result["products"] = products
        
        price_cards = parse_price_cards(soup)
        if price_cards:
            result["pricing"] = price_cards
    else:
        result["note"] = "Dynamic pricing requires date selection on website"
    
    return result


def get_rentals():
    """Fetch and parse rental prices from all Blue Mountain rental pages."""
    results = {}
    driver = None
    
    try:
        driver = get_driver()
        
        for category, url in URLS.items():
            try:
                data = get_rentals_from_url(driver, url, category)
                results[category] = data
            except Exception as e:
                print(f"Error fetching {category}: {e}")
                results[category] = {"error": str(e)}
    finally:
        if driver:
            driver.quit()
    
    return results


def main():
    rentals = get_rentals()
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(rentals, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
