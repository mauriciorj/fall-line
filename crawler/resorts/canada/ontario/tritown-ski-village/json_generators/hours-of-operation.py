import json
import os
import re
import time
import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

PAGE_URL = "https://tritownskivillage.ca/"
RESORT_ID = "tritown-ski-village"
HEADERS = {"User-Agent": "Mozilla/5.0"}
DAYS = ("sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday")

def get_hours():
    r = requests.get(PAGE_URL, headers=HEADERS, timeout=30); r.raise_for_status()
    text = " ".join(BeautifulSoup(r.content, "html.parser").get_text(" ", strip=True).split()).lower()
    match = re.search(r"hours of operation:\s*saturday and sunday:\s*([^ ]+\s*[^ ]+\s*[-–]\s*[^ ]+\s*[^ ]+)", text)
    if not match: raise ValueError("Could not find Hours of Operation HTML")
    hours = {day: "closed" for day in DAYS}; hours["saturday"] = hours["sunday"] = match.group(1).replace("a.m.", "am").replace("p.m.", "pm")
    return hours

def main():
    payload = {"hours": get_hours(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    with open(os.path.join(os.path.dirname(__file__), "hours-of-operation.json"), "w", encoding="utf-8") as f: json.dump(payload, f, indent=2)
if __name__ == "__main__": main()
