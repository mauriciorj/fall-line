"""
Glen Eden Rentals Crawler
Scrapes rental rates from https://gleneden.on.ca/plan-your-visit/
"""

import json
import os
import re
import sys
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from convex_client import push_resort_rentals
from dtos import to_rentals_dto

RESORT_ID = "glen-eden"
SOURCE_URL = "https://gleneden.on.ca/plan-your-visit/"


def fetch_page(url: str) -> str:
    """Fetch the HTML content from the given URL."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text


def is_price(text: str) -> bool:
    """Check if text looks like a price."""
    return bool(re.search(r'\$\d+', text))


def parse_rentals(html: str) -> dict:
    """Parse rental rates from the HTML content."""
    soup = BeautifulSoup(html, "html.parser")
    
    result = {
        "rental_daily_packages": [],
        "rental_single_items": [],
        "rental_lesson_packages": [],
    }

    tables = soup.find_all("table")

    for table in tables:
        # Get all rows including header
        all_rows = table.find_all("tr")
        if not all_rows:
            continue

        # Get header cells
        header_row = all_rows[0]
        headers = [cell.get_text(strip=True).lower() for cell in header_row.find_all(["th", "td"])]
        
        # Identify table type based on headers
        header_text = " ".join(headers)
        
        # Check if this is a lift ticket table (has peak/off-peak or age columns)
        is_lift_ticket_table = (
            ("peak" in header_text and "off" in header_text) or
            ("age" in header_text and any(is_price(cell.get_text()) for row in all_rows[1:] for cell in row.find_all(["td", "th"])))
        )
        
        # Check if this is a rental rates table
        is_rental_table = "rate" in header_text and not is_lift_ticket_table
        
        if is_rental_table:
            # Parse rental rates
            for row in all_rows[1:]:
                cells = [cell.get_text(strip=True) for cell in row.find_all(["td", "th"])]
                if len(cells) >= 2 and cells[0]:
                    has_price = any(is_price(c) for c in cells)
                    if not has_price:
                        continue
                    
                    item_name = cells[0]
                    price = next((c for c in cells[1:] if is_price(c)), None)
                    
                    if "lesson" in item_name.lower():
                        result["rental_lesson_packages"].append({
                            "item": item_name,
                            "price": price
                        })
                    elif any(word in item_name.lower() for word in ["helmet", "poles", "boots", "skis", "snowboard"]):
                        result["rental_single_items"].append({
                            "item": item_name,
                            "price": price
                        })
                    else:
                        result["rental_daily_packages"].append({
                            "item": item_name,
                            "price": price
                        })

    return result


def get_rentals(url: str = "https://gleneden.on.ca/plan-your-visit/") -> dict:
    """Main function to fetch and parse rental rates from Glen Eden."""
    html = fetch_page(url)
    return parse_rentals(html)


if __name__ == "__main__":
    print("Fetching rental rates from Glen Eden...")
    try:
        data = get_rentals()
        output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved to {output_file}")
        result = push_resort_rentals(
            RESORT_ID,
                SOURCE_URL,
            to_rentals_dto(data),
            updated_at_ms=int(time.time() * 1000),
        )
        if result is not None:
            print("Pushed to Convex:", result)
    except requests.RequestException as e:
        print(f"Error fetching page: {e}")
    except Exception as e:
        print(f"Error parsing rates: {e}")
