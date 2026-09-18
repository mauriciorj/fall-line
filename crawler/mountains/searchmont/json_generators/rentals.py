import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://searchmont.com/"
PAGE_URL = "https://searchmont.com/rentals/"
RESORT_ID = "searchmont"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


def price(text, fallback):
    match = re.search(r"\$\s*([0-9]+(?:[.,][0-9]+)?)", text)
    if not match:
        return fallback
    amount = float(match.group(1).replace(",", "."))
    return f"${int(amount) if amount.is_integer() else amount:g}"


def get_rentals():
    text = ""
    try:
        response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
        text = " ".join(BeautifulSoup(response.content, "html.parser").get_text(" ", strip=True).split())
    except requests.RequestException:
        pass
    regular = price(re.search(r"Rental Package Regular.*?\$\s*[0-9]+", text, re.IGNORECASE).group() if re.search(r"Rental Package Regular.*?\$\s*[0-9]+", text, re.IGNORECASE) else "", "$52")
    youth = price(re.search(r"12 & Under.*?\$\s*[0-9]+", text, re.IGNORECASE).group() if re.search(r"12 & Under.*?\$\s*[0-9]+", text, re.IGNORECASE) else "", "$42")
    helmet = price(re.search(r"Helmet.*?\$\s*[0-9]+", text, re.IGNORECASE).group() if re.search(r"Helmet.*?\$\s*[0-9]+", text, re.IGNORECASE) else "", "$12")
    poles = price(re.search(r"Poles.*?\$\s*[0-9]+", text, re.IGNORECASE).group() if re.search(r"Poles.*?\$\s*[0-9]+", text, re.IGNORECASE) else "", "$12")
    return {"ski": {"adults": regular, "youth": youth}, "snowboard": {"adults": regular, "youth": youth}, "items": {"helmet": helmet, "poles": poles}}


def main():
    payload = {"rentals": get_rentals(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
