import json
import os
import re
import time
import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

PAGE_URL = "https://tritownskivillage.ca/?page_id=691"
RESORT_ID = "tritown-ski-village"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def price(text):
    m = re.search(r"\$\s*([0-9]+(?:\.[0-9]+)?)", text)
    if not m: raise ValueError(f"Missing price: {text}")
    return f"${m.group(1)}"

def get_rentals():
    r = requests.get(PAGE_URL, headers=HEADERS, timeout=30); r.raise_for_status(); text = " ".join(BeautifulSoup(r.content, "html.parser").get_text(" ", strip=True).split())
    package = price(re.search(r"Full Ski Package.*?\$\s*[0-9.]+", text, re.I).group()); board = price(re.search(r"Full Snowboard Package.*?\$\s*[0-9.]+", text, re.I).group()); item = price(re.search(r"Skis/Snowboard Only.*?\$\s*[0-9.]+", text, re.I).group()); boots = price(re.search(r"Boots Only.*?\$\s*[0-9.]+", text, re.I).group())
    return {"ski": {"adults": package, "youth": package}, "snowboard": {"adults": board, "youth": board}, "items": {"skis": item, "snowboard": item, "boots": boots}}

def main():
    payload = {"rentals": get_rentals(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    with open(os.path.join(os.path.dirname(__file__), "rentals.json"), "w", encoding="utf-8") as f: json.dump(payload, f, indent=2)
if __name__ == "__main__": main()
