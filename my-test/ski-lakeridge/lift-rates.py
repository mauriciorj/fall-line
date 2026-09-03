import requests
from bs4 import BeautifulSoup
import json
import os

URL = "https://ski-lakeridge.com/skiing-snowboarding/hours-ticket-prices/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def extract_table_data(table):
    """General function to extract table data into a list of dictionaries."""
    data = []
    headers = []
    
    thead = table.find('thead')
    if thead:
        headers = [th.get_text(strip=True) for th in thead.find_all(['th', 'td'])]
    else:
        # If no thead, assume first row contains headers
        first_row = table.find('tr')
        if first_row:
            headers = [th.get_text(strip=True) for th in first_row.find_all(['th', 'td'])]

    rows = table.find_all('tr')
    for row in rows:
        if row.find('th'): # Skip header rows
            continue
        cells = row.find_all('td')
        if cells:
            row_data = [cell.get_text(strip=True) for cell in cells]
            # Handle cases where rows might be missing columns by padding with empty strings
            while len(row_data) < len(headers):
                row_data.append("")
                
            entry = {}
            for i in range(min(len(headers), len(row_data))):
                key = headers[i] if headers[i] else f"Column_{i+1}"
                entry[key] = row_data[i]
            data.append(entry)
            
    return data

def main():
    print(f"Fetching {URL}...")
    response = requests.get(URL, headers=HEADERS)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    result = {}

    # Reusable function to extract ticket tables based on h2 text
    def extract_ticket_section(heading_text, key_name):
        heading = soup.find('h2', string=lambda text: text and heading_text.lower() in text.lower())
        if heading:
            table = heading.find_next('table')
            if table:
                result[key_name] = extract_table_data(table)

    extract_ticket_section("Beginner Area Ticket Prices", "Beginner Area Ticket Prices (Magic Carpet Only)")
    extract_ticket_section("Monday to Wednesday Lift Tickets", "Monday to Wednesday Lift Tickets (NOT VALID ON FAMILY DAY)")
    extract_ticket_section("Thursday to Sunday Lift Tickets", "Thursday to Sunday Lift Tickets")

    output_file = os.path.join(os.path.dirname(__file__), "lift-rates.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")

if __name__ == "__main__":
    main()
