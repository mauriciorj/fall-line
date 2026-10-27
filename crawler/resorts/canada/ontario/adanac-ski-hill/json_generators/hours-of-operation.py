import json
import os
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.greatersudbury.ca/play/ski-hills/adanac-ski-hill/hours/"
RESORT_ID = "adanac-ski-hill"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


def normalize_text(value):
    return " ".join(value.lower().split())


def parse_schedule(heading):
    list_element = heading.find_next("ul")
    if not list_element:
        raise ValueError("Missing half-day hours list")
    values = [normalize_text(item.get_text(" ", strip=True)) for item in list_element.find_all("li")]
    if not values:
        raise ValueError("Missing half-day hours values")
    return " / ".join(values)


def get_hours():
    response = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    section = next((heading for heading in soup.find_all(["h2", "h3", "h4"]) if normalize_text(heading.get_text(" ", strip=True)).startswith("ski hill hours for half day passes")), None)
    if not section:
        raise ValueError("Could not find Ski Hill Hours for Half Day Passes section")
    weekday_heading = next((heading for heading in section.find_all_next(["h3", "h4"]) if normalize_text(heading.get_text(" ", strip=True)) == "wednesdays to fridays:"), None)
    weekend_heading = next((heading for heading in section.find_all_next(["h3", "h4"]) if normalize_text(heading.get_text(" ", strip=True)) == "saturdays and sundays:"), None)
    if not weekday_heading or not weekend_heading:
        raise ValueError("Could not find Adanac weekday/weekend half-day headings")
    weekday_hours = parse_schedule(weekday_heading)
    weekend_hours = parse_schedule(weekend_heading)
    return {
        "sunday": weekend_hours,
        "monday": "closed",
        "tuesday": "closed",
        "wednesday": weekday_hours,
        "thursday": weekday_hours,
        "friday": weekday_hours,
        "saturday": weekend_hours,
    }


def main():
    payload = {"hours": get_hours(), "resortId": RESORT_ID, "sourceUrl": SOURCE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
