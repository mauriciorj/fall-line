import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.devilsglen.com"
PAGE_URL = f"{SOURCE_URL}/About/Directions_Hours"
RESORT_ID = "devils-glen"
DAYS = (
    "sunday",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
)
DAY_INDEX = {day: index for index, day in enumerate(DAYS)}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}


def fetch_soup():
    response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser")


def normalize_text(value):
    return " ".join(value.lower().split())


def normalize_time(value):
    value = normalize_text(value).replace(" am", "am").replace(" pm", "pm")
    value = re.sub(r"\s*[-–]\s*", " to ", value)
    return value


def parse_days(label):
    label = normalize_text(label)
    if "midweek" in label:
        return ["monday", "tuesday", "wednesday", "thursday", "friday"]
    if "saturday" in label:
        return ["saturday"]
    if "sunday" in label:
        return ["sunday"]
    return []


def get_hours():
    soup = fetch_soup()
    heading = next(
        (
            element
            for element in soup.find_all(["h2", "h3", "h4"])
            if normalize_text(element.get_text(" ", strip=True)).startswith("lifts")
        ),
        None,
    )
    if not heading:
        raise ValueError("Could not find lifts hours section")

    paragraph = heading.find_next("p")
    if not paragraph:
        raise ValueError("Could not find lifts hours values")

    hours = {day: "closed" for day in DAYS}
    for line in paragraph.stripped_strings:
        if "*the calendar" in normalize_text(line):
            continue
        match = re.match(r"(.+?)\s+(\d{1,2}:\d{2}\s*[-–]\s*\d{1,2}:\d{2})$", line)
        if not match:
            continue
        value = normalize_time(match.group(2))
        for day in parse_days(match.group(1)):
            hours[day] = value

    if all(value == "closed" for value in hours.values()):
        raise ValueError("Could not parse lifts hours")
    return hours


def main():
    payload = {
        "hours": get_hours(),
        "resortId": RESORT_ID,
        "sourceUrl": PAGE_URL,
        "updatedAt": int(time.time() * 1000),
    }
    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
