import json
import os
import re
import time

import requests
from bs4 import BeautifulSoup
import truststore

truststore.inject_into_ssl()

RESORT_ID = "panorama"
URLS = {
    "ski": "https://www.panoramaresort.com/while-you-are-here/ski-bike-and-equipment-rentals/ski-rentals",
    "snowboard": "https://www.panoramaresort.com/while-you-are-here/ski-bike-and-equipment-rentals/snowboard-rentals",
}
HEADERS = {"User-Agent": "Mozilla/5.0"}


def parse_price(value):
    match = re.search(r"\$\s*([0-9]+(?:[.,][0-9]+)?)", value)
    if not match:
        return None
    amount = float(match.group(1).replace(",", ""))
    return f"${int(amount) if amount.is_integer() else amount:g}"


def get_package_price(html):
    soup = BeautifulSoup(html, "html.parser")
    for table in soup.find_all("table"):
        text = " ".join(table.stripped_strings)
        if "Adult/Youth" not in text or "1 Day" not in text:
            continue
        for row in table.find_all("tr"):
            cells = [" ".join(cell.stripped_strings) for cell in row.find_all(["th", "td"])]
            if cells and "Adult/Youth" in cells[0] and len(cells) > 1:
                return parse_price(cells[2] if cells[1].lower() == "1 day" else " ".join(cells[1:]))
        match = re.search(r"Adult/Youth[^$]*\$\s*([0-9]+)", text)
        if match:
            return f"${match.group(1)}"
    raise ValueError("Could not find Adult/Youth 1 Day rental price in HTML")


def get_rentals():
    rentals = {}
    for rental_type, url in URLS.items():
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        rentals[rental_type] = {"adults": get_package_price(response.content.decode(response.encoding or "utf-8", errors="replace"))}
    rentals["items"] = {}
    return rentals


def main():
    payload = {"rentals": get_rentals(), "resortId": RESORT_ID, "sourceUrl": URLS["ski"], "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
