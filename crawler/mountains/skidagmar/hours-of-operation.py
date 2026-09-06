import json
import re
import os

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

URL = "https://www.skidagmar.com/alpine-rates/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def extract_hours(soup):
    """Extract hours of operation from the bottom of the page."""
    hours_heading = soup.find(string=re.compile(r"Hours of Operation", re.I))
    if not hours_heading:
        return {}

    # Walk up to the container div
    container = hours_heading.find_parent()
    for _ in range(5):
        container = container.find_parent()
        text = container.get_text(strip=True)
        if "Monday" in text and "Sunday" in text:
            break

    # Find the <p> that contains the day schedule lines
    hours = {}
    for p in container.find_all("p"):
        text = p.get_text(separator="\n", strip=True)
        if "Monday" in text:
            for line in text.split("\n"):
                line = line.strip()
                if " - " in line:
                    day, time = line.split(" - ", 1)
                    hours[day.strip()] = time.strip()
            break
    return hours


def get_rates():
    """Fetch and parse all rates from Ski Dagmar."""
    print(f"Fetching {URL}...")
    response = requests.get(URL, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")

    return extract_hours(soup)


def main():
    rates = get_rates()
    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(rates, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
