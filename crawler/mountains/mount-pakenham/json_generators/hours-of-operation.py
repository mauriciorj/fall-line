import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://shop.mountpakenham.com/"
PAGE_URL = "https://shop.mountpakenham.com/pages/skiing-snowboarding"
RESORT_ID = "mount-pakenham"
DAYS = ("sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday")
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


def normalize_text(value):
    return " ".join(value.replace("\xa0", " ").split()).lower()


def normalize_time(value):
    value = normalize_text(value).replace("a.m.", "am").replace("p.m.", "pm")
    if "closed" in value:
        return "closed"
    value = re.sub(r"\s*[-–—]\s*", " to ", value)
    return re.sub(r"\s+(am|pm)\b", r"\1", value)


def get_hours():
    response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    text = normalize_text(BeautifulSoup(response.content, "html.parser").get_text(" ", strip=True))
    start = text.find("hours of operation")
    if start == -1:
        raise ValueError("Could not find Hours of Operation section")
    section = text[start:].split("equipment:", 1)[0]
    hours = {day: None for day in DAYS}
    if "closed mondays" in text:
        hours["monday"] = "closed"

    weekday_match = re.search(r"tuesday\s*[-–—]\s*saturday\s*[-–—]\s*(.+?)(?=\s+sunday\s*[-–—])", section)
    if weekday_match:
        for day in ("tuesday", "wednesday", "thursday", "friday", "saturday"):
            hours[day] = normalize_time(weekday_match.group(1))

    sunday_match = re.search(r"sunday\s*[-–—]\s*(.+?)(?=\s+december\s+24|$)", section)
    if sunday_match:
        hours["sunday"] = normalize_time(sunday_match.group(1))

    missing = {day for day, value in hours.items() if value is None}
    if missing:
        raise ValueError(f"Missing Mount Pakenham hours weekdays: {sorted(missing)}")
    return {day: hours[day] for day in DAYS}


def main():
    payload = {"hours": get_hours(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
