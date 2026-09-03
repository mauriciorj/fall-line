import requests
from bs4 import BeautifulSoup
import json
import os

URL = "https://www.skidagmar.com/alpine-rates/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Mapping of table index to the h3 section it belongs under (rentals only)
TABLE_SECTIONS = {
    5: "Equipment Rentals - Package",
    6: "Equipment Rentals - Separate Items",
    7: "Lockers",
}


def extract_table_data(table):
    """Extract table rows into a list of dictionaries using thead as keys."""
    headers = []
    thead = table.find("thead")
    if thead:
        headers = [
            th.get_text(strip=True) for th in thead.find_all(["th", "td"])
        ]

    rows = []
    for tr in table.find("tbody").find_all("tr") if table.find("tbody") else table.find_all("tr"):
        cells = tr.find_all("td")
        if not cells:
            continue
        values = [cell.get_text(strip=True) for cell in cells]
        # Skip completely empty rows
        if not any(values):
            continue
        if headers:
            row = {}
            for i, val in enumerate(values):
                key = headers[i] if i < len(headers) and headers[i] else f"Column_{i+1}"
                row[key] = val
            rows.append(row)
        else:
            rows.append(values)
    return rows


def get_rentals():
    """Fetch and parse rental rates from Ski Dagmar."""
    print(f"Fetching {URL}...")
    response = requests.get(URL, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    tables = soup.find_all("table", class_="table")
    result = {}

    for i, table in enumerate(tables):
        section = TABLE_SECTIONS.get(i)
        if section is None:
            continue
        data = extract_table_data(table)
        if data:
            result[section] = data

    return result


def main():
    rentals = get_rentals()
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(rentals, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
