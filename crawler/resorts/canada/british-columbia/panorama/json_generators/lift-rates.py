import json
import os
import re
import time

import requests
from bs4 import BeautifulSoup
import truststore

truststore.inject_into_ssl()

RESORT_ID = "panorama"
SOURCE_URL = "https://www.panoramaresort.com/planning/tickets-and-passes/lift-tickets"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def parse_rates(html):
    soup = BeautifulSoup(html, "html.parser")
    for table in soup.find_all("table"):
        text = " ".join(table.stripped_strings)
        if "WINDOW TICKET" not in text or "1 Day" not in text:
            continue
        for row in table.find_all("tr"):
            cells = [" ".join(cell.stripped_strings) for cell in row.find_all(["th", "td"])]
            if not cells or not cells[0].startswith("1 Day"):
                continue
            prices = [re.search(r"\$\s*([0-9,]+)", cell) for cell in cells]
            values = [match.group(1).replace(",", "") for match in prices if match]
            if values:
                return {"day-week": {"adults": f"${values[0]}"}}
    raise ValueError("Could not find WINDOW TICKET 1 Day rate in HTML")


def get_lift_rates():
    response = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return parse_rates(response.content.decode(response.encoding or "utf-8", errors="replace"))


def main():
    payload = {"rates": get_lift_rates(), "resortId": RESORT_ID, "sourceUrl": SOURCE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "lift-rates.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
