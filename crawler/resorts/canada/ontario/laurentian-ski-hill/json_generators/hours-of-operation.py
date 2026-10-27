import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

RESORT_ID = "laurentian-ski-hill-north-bay"
SOURCE_URL = "https://laurentianskihill.com/hours/"
DAYS = ("sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday")
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


def normalize_text(value):
    return " ".join(value.lower().split())


def normalize_time(value):
    normalized = normalize_text(value)
    if "closed" in normalized:
        return "closed"
    match = re.search(r"open\s*\(([^)]+)\)", normalized)
    if match:
        normalized = match.group(1)
    return re.sub(r"\s*[-–]\s*", " to ", normalized)


def get_hours():
    response = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    heading = next((element for element in soup.find_all(["h2", "h3", "h4"]) if normalize_text(element.get_text(" ", strip=True)) == "spring operating hours"), None)
    if not heading:
        raise ValueError("Could not find Spring Operating Hours section")

    hours = {}
    for element in heading.find_all_next(["h2", "h3", "h4"]):
        if element.name == "h2":
            break
        match = re.match(r"^(\w+)\s*-\s*(.+)$", normalize_text(element.get_text(" ", strip=True)))
        if not match or match.group(1) not in DAYS:
            continue
        hours[match.group(1)] = normalize_time(match.group(2))

    missing = set(DAYS) - hours.keys()
    if missing:
        raise ValueError(f"Missing weekday hours: {sorted(missing)}")
    return {day: hours[day] for day in DAYS}


def main():
    payload = {"hours": get_hours(), "resortId": RESORT_ID, "sourceUrl": SOURCE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
