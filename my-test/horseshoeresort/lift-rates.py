import requests
from bs4 import BeautifulSoup
import json
import re
import os


def get_lift_rates():
    """
    Crawl Horseshoe Resort's lift ticket pricing page.
    Returns a dictionary with lift ticket rates.
    """
    url = "https://horseshoeresort.com/ski/lift-ticket-and-rentals-pricing/"
    
    request_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, headers=request_headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    data = {
        "lift_tickets": []
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
        
        # Skip rental tables
        is_rental = "rental" in heading_text.lower() or "rental" in " ".join(headers).lower()
        if is_rental:
            continue
        
        # Parse ticket type from heading
        ticket_type = None
        if "day & night" in heading_text.lower():
            ticket_type = "day_and_night"
        elif "day ticket" in heading_text.lower():
            ticket_type = "day"
        elif "night ticket" in heading_text.lower():
            ticket_type = "night"
        
        # Process data rows
        for row in rows[1:]:
            cells = row.find_all(["td", "th"])
            if len(cells) < 2:
                continue
            
            # Lift ticket table has 3 columns: Age Group, Midweek, Weekend
            if len(cells) >= 3:
                age_group = cells[0].get_text(strip=True)
                midweek_price = cells[1].get_text(strip=True)
                weekend_price = cells[2].get_text(strip=True)
                
                # Extract time from heading
                time_match = re.search(r'\(([^)]+)\)', heading_text)
                time_range = time_match.group(1) if time_match else ""
                
                data["lift_tickets"].append({
                    "ticket_type": ticket_type,
                    "time_range": time_range,
                    "age_group": age_group,
                    "midweek_price": midweek_price,
                    "weekend_price": weekend_price
                })
    
    return data


def main():
    print("Fetching Horseshoe Resort lift rates...")
    rates = get_lift_rates()
    output_file = os.path.join(os.path.dirname(__file__), "lift-rates.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(rates, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")
    return rates


if __name__ == "__main__":
    main()
