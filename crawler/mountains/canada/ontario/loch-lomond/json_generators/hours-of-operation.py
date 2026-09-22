import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.lochlomond.ca/"
PAGE_URL = "https://www.lochlomond.ca/hill-hours/"
RESORT_ID = "loch-lomond"
DAYS = ("sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday")
DAY_INDEX = {
    "sun": 0,
    "sunday": 0,
    "mon": 1,
    "monday": 1,
    "tue": 2,
    "tues": 2,
    "tuesday": 2,
    "wed": 3,
    "wednesday": 3,
    "thu": 4,
    "thur": 4,
    "thurs": 4,
    "thursday": 4,
    "fri": 5,
    "friday": 5,
    "sat": 6,
    "saturday": 6,
}
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}
CLOSED_MESSAGE = "our ski area is now closed for the season. see you next winter!"


def normalize_text(value):
    return " ".join(value.replace("\xa0", " ").split()).lower()


def normalize_time(value):
    value = normalize_text(value)
    if "closed" in value:
        return "closed"
    return re.sub(r"\s*[-–—]\s*", " to ", value)


def expand_days(value):
    indexes = [DAY_INDEX[day] for day in re.findall(r"\b(?:sun(?:day)?|mon(?:day)?|tues?(?:day)?|wed(?:nesday)?|thurs?(?:day)?|fri(?:day)?|sat(?:urday)?)\b", value)]
    if len(indexes) >= 2 and re.search(r"[-–—]", value):
        start, end = indexes[:2]
        return [DAYS[index] for index in range(start, end + 1)]
    return [DAYS[index] for index in indexes]


def get_hours():
    response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    page_text = normalize_text(soup.get_text(" ", strip=True))
    if CLOSED_MESSAGE in page_text:
        return {day: "closed" for day in DAYS}

    hours = {}
    table = soup.find("table")
    if not table:
        raise ValueError("Could not find hill hours table")
    for row in table.find_all("tr"):
        cells = row.find_all(["th", "td"])
        if len(cells) < 2:
            continue
        for day in expand_days(cells[0].get_text(" ", strip=True)):
            hours[day] = normalize_time(cells[1].get_text(" ", strip=True))

    missing = set(DAYS) - hours.keys()
    if missing:
        raise ValueError(f"Missing hill hours weekdays: {sorted(missing)}")
    return {day: hours[day] for day in DAYS}


def main():
    payload = {"hours": get_hours(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
