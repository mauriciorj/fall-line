import json
import os
import re
import time
import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

PAGE_URL = "https://tritownskivillage.ca/?page_id=476"
RESORT_ID = "tritown-ski-village"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def price(text):
    m = re.search(r"\$\s*([0-9]+(?:\.[0-9]+)?)", text)
    if not m: raise ValueError(f"Missing price: {text}")
    return f"${m.group(1)}"

def get_lift_rates():
    r = requests.get(PAGE_URL, headers=HEADERS, timeout=30); r.raise_for_status(); s = BeautifulSoup(r.content, "html.parser")
    text = " ".join(s.get_text(" ", strip=True).split())
    adult = price(re.search(r"Adult Full Day Pass.*?\$\s*[0-9.]+", text, re.I).group())
    youth = price(re.search(r"Youth Full Day Pass.*?\$\s*[0-9.]+", text, re.I).group())
    return {"day-week": {"adults": adult, "youth": youth, "seniors": youth}, "day-weekend": {"adults": adult, "youth": youth, "seniors": youth}}

def main():
    payload = {"rates": get_lift_rates(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    with open(os.path.join(os.path.dirname(__file__), "lift-rates.json"), "w", encoding="utf-8") as f: json.dump(payload, f, indent=2)
if __name__ == "__main__": main()
