import json
import os
import re
import time

import requests
from bs4 import BeautifulSoup
import truststore

truststore.inject_into_ssl()

RESORT_ID = "sun-peaks-resort"
SOURCE_URL = "https://www.sunpeaksresort.com/ski-ride/the-mountain/winter-hours-of-operation"
DAYS = ("sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday")


def get_hours():
    response = requests.get(SOURCE_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    response.raise_for_status()
    text = " ".join(BeautifulSoup(response.content, "html.parser").stripped_strings)
    match = re.search(r"(?:Burfield Chairlift|Crystal Chairlift).*?(\d{1,2}:\d{2}am\s+to\s+\d{1,2}:\d{2}pm)", text, re.IGNORECASE)
    if not match:
        raise ValueError("Could not find daily lift hours in HTML")
    return {day: match.group(1).lower() for day in DAYS}


def main():
    payload = {"hours": get_hours(), "resortId": RESORT_ID, "sourceUrl": SOURCE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
