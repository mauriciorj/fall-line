import json
import re
import os
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

RESORT_ID = "horseshoe-valley-resort"
RESORT_NAME = "Horseshoe Valley Resort"
SOURCE_URL = "https://horseshoeresort.com/ski/lift-ticket-and-rentals-pricing/"


def get_rentals():
    """
    Crawl Horseshoe Resort's rentals pricing page.
    Returns a dictionary with rental prices.
    """
    url = SOURCE_URL
    
    request_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, headers=request_headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    data = {
        "rentals": []
    }
    
    tables = soup.find_all("table")
    
    for table in tables:
        # Find preceding heading to identify the table type
        prev_heading = table.find_previous(["h3", "h4"])
        heading_text = prev_heading.get_text(strip=True) if prev_heading else ""
        
        rows = table.find_all("tr")
        if not rows:
            continue
        
        # Get header row
        header_cells = rows[0].find_all(["th", "td"])
        headers = [cell.get_text(strip=True) for cell in header_cells]
        
        # Only process rental tables
        is_rental = "rental" in heading_text.lower() or "rental" in " ".join(headers).lower()
        if not is_rental:
            continue
        
        # Process data rows
        for row in rows[1:]:
            cells = row.find_all(["td", "th"])
            if len(cells) < 2:
                continue
            
            # Rental table has 4 columns: Package, Age, Midweek, Weekend
            if len(cells) >= 4:
                package = cells[0].get_text(strip=True)
                # Clean up package name
                package = re.sub(r'\*.*$', '', package).strip()
                
                age_group = cells[1].get_text(strip=True)
                midweek_price = cells[2].get_text(strip=True)
                weekend_price = cells[3].get_text(strip=True)
                
                data["rentals"].append({
                    "item": package,
                    "age_group": age_group,
                    "midweek_price": midweek_price,
                    "weekend_price": weekend_price
                })
    
    return data


def main():
    print("Fetching Horseshoe Resort rentals...")
    rentals = get_rentals()
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(rentals, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")

    result = push_resort_rentals(
        RESORT_ID,
        RESORT_NAME,
        SOURCE_URL,
        to_rentals_dto(rentals),
        fetched_at_ms=int(time.time() * 1000),
    )
    if result is not None:
        print("Pushed to Convex:", result)

    return rentals


if __name__ == "__main__":
    main()
