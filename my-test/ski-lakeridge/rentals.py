import json
import os

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

URL = "https://ski-lakeridge.com/skiing-snowboarding/equipment-rentals/"
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
        if row.find('th'):  # Skip header rows
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


def get_rentals():
    """Fetch and parse equipment rental rates from Ski Lakeridge."""
    print(f"Fetching {URL}...")
    response = requests.get(URL, headers=HEADERS)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    result = {}

    # Find all tables on the page
    tables = soup.find_all('table')
    
    for table in tables:
        # Try to find a heading before the table
        heading = table.find_previous(['h2', 'h3', 'h4'])
        if heading:
            section_name = heading.get_text(strip=True)
        else:
            section_name = f"Rentals_{len(result) + 1}"
        
        table_data = extract_table_data(table)
        if table_data:
            result[section_name] = table_data

    return result


def main():
    rentals = get_rentals()
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(rentals, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
