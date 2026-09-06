"""
Glen Eden Lift Rates Crawler
Scrapes lift ticket rates from https://gleneden.on.ca/plan-your-visit/
"""

import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional
import json
import re
import os


@dataclass
class LiftTicketRate:
    category: str
    age_range: str
    peak_online: Optional[str]
    peak_gate: Optional[str]
    off_peak_online: Optional[str]
    off_peak_gate: Optional[str]


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


def parse_lift_rates(html: str) -> dict:
    """Parse lift rates from the HTML content."""
    soup = BeautifulSoup(html, "html.parser")
    
    result = {
        "lift_tickets": [],
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
        
        if is_lift_ticket_table:
            # Parse lift ticket rates
            for row in all_rows[1:]:
                cells = [cell.get_text(strip=True) for cell in row.find_all(["td", "th"])]
                if len(cells) >= 2 and cells[0]:
                    # Skip header-like rows
                    if cells[0].lower() in ["lift tickets", ""]:
                        continue
                    
                    # Check if any cell has a price
                    has_price = any(is_price(c) for c in cells)
                    if not has_price:
                        continue
                    
                    rate_data = {
                        "category": cells[0],
                        "age_range": cells[1] if len(cells) > 1 else None,
                    }
                    
                    # Handle different column structures
                    if len(cells) >= 6:
                        # Full table: category, age, peak_online, peak_gate, off_peak_online, off_peak_gate
                        rate_data["peak_online"] = cells[2] if len(cells) > 2 else None
                        rate_data["peak_gate"] = cells[3] if len(cells) > 3 else None
                        rate_data["off_peak_online"] = cells[4] if len(cells) > 4 else None
                        rate_data["off_peak_gate"] = cells[5] if len(cells) > 5 else None
                    elif len(cells) >= 4:
                        # Simpler table: category, age, peak, off_peak
                        rate_data["peak_online"] = cells[2] if len(cells) > 2 else None
                        rate_data["off_peak_online"] = cells[3] if len(cells) > 3 else None
                    elif len(cells) >= 3:
                        rate_data["peak_online"] = cells[2] if len(cells) > 2 else None
                    
                    result["lift_tickets"].append(rate_data)

    return result


def get_lift_rates(url: str = "https://gleneden.on.ca/plan-your-visit/") -> dict:
    """Main function to fetch and parse lift rates from Glen Eden."""
    html = fetch_page(url)
    return parse_lift_rates(html)




if __name__ == "__main__":
    print("Fetching lift rates from Glen Eden...")
    try:
        data = get_lift_rates()
        output_file = os.path.join(os.path.dirname(__file__), "lift-rates.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved to {output_file}")
    except requests.RequestException as e:
        print(f"Error fetching page: {e}")
    except Exception as e:
        print(f"Error parsing rates: {e}")
