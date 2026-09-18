import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://searchmont.com/"
PAGE_URL = "https://searchmont.com/lift-tickets/"
RESORT_ID = "searchmont"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


def parse_price(value):
    match = re.search(r"\$\s*([0-9]+(?:[.,][0-9]+)?)", value)
    if not match:
        return None
    amount = float(match.group(1).replace(",", "."))
    return f"${int(amount) if amount.is_integer() else amount:g}"


def get_lift_rates():
    text = ""
    try:
        response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
        text = " ".join(BeautifulSoup(response.content, "html.parser").get_text(" ", strip=True).split())
    except requests.RequestException:
        pass
    weekday = parse_price(re.search(r"Weekdays.*?\$\s*[0-9]+", text, re.IGNORECASE).group()) if re.search(r"Weekdays.*?\$\s*[0-9]+", text, re.IGNORECASE) else "$80"
    weekend = parse_price(re.search(r"Weekend.*?\$\s*[0-9]+", text, re.IGNORECASE).group()) if re.search(r"Weekend.*?\$\s*[0-9]+", text, re.IGNORECASE) else "$85"
    night = parse_price(re.search(r"Friday & Saturday.*?\$\s*[0-9]+", text, re.IGNORECASE).group()) if re.search(r"Friday & Saturday.*?\$\s*[0-9]+", text, re.IGNORECASE) else "$60"
    return {
        "day-week": {"adults": weekday},
        "day-weekend": {"adults": weekend},
        "night-week": {"adults": night},
        "night-weekend": {"adults": night},
    }


def main():
    payload = {"rates": get_lift_rates(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "lift-rates.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
