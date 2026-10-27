import json
import os
import re
import time

import requests
from bs4 import BeautifulSoup
import truststore

truststore.inject_into_ssl()

RESORT_ID = "sun-peaks-resort"
SOURCE_URL = "https://www.sunpeaksresort.com/ski-ride/sports-school-rentals/rental-equipment/sun-peaks-rentals"


def parse_adult_price(html):
    soup = BeautifulSoup(html, "html.parser")
    for table in soup.find_all("table"):
        text = " ".join(table.stripped_strings)
        if "Standard Ski or Snowboard Package" not in text or "Adult (13+)" not in text:
            continue
        for row in table.find_all("tr"):
            cells = [" ".join(cell.stripped_strings) for cell in row.find_all(["th", "td"])]
            if cells and "Standard Ski or Snowboard Package" in cells[0]:
                match = re.search(r"\$\s*([0-9]+)", " ".join(cells[1:]))
                if match:
                    return f"${match.group(1)}"
    raise ValueError("Could not find Standard Ski or Snowboard Package adult price in HTML")


def get_rentals():
    response = requests.get(SOURCE_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    response.raise_for_status()
    price = parse_adult_price(response.content.decode(response.encoding or "utf-8", errors="replace"))
    return {"ski": {"adults": price}, "snowboard": {"adults": price}, "items": {}}


def main():
    payload = {"rentals": get_rentals(), "resortId": RESORT_ID, "sourceUrl": SOURCE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
