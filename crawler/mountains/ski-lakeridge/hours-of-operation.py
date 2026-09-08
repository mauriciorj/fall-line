import json
import os
import sys
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from convex_client import push_resort_hours
from dtos import to_hours

URL = "https://ski-lakeridge.com/skiing-snowboarding/hours-ticket-prices/"
RESORT_ID = "lakeridge-ski-resort"
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

    # Extract Hours of operation
    # Find the th containing "Date of operation"
    date_th = soup.find('th', string=lambda text: text and "Date of operation" in text)
    if date_th:
        hours_table = date_th.find_parent('table')
        if hours_table:
            result["Hours of operation"] = extract_table_data(hours_table)

    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")

    push_result = push_resort_hours(
        RESORT_ID,
        URL,
        to_hours(result),
        updated_at_ms=int(time.time() * 1000),
    )
    if push_result is not None:
        print("Pushed to Convex:", push_result)

if __name__ == "__main__":
    main()
