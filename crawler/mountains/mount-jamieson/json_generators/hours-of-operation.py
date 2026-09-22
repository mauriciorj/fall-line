import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.mountjamieson.ca/"
PAGE_URL = "https://www.mountjamieson.ca/"
RESORT_ID = "mount-jamieson"
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


def normalize_text(value):
    return " ".join(value.replace("\xa0", " ").split()).lower()


def normalize_time(value):
    value = normalize_text(value)
    if "closed" in value:
        return "closed"
    value = value.replace("a.m.", "am").replace("p.m.", "pm")
    value = re.sub(r"\s*[-–—]\s*", " to ", value)
    return re.sub(r"\s+(am|pm)\b", r"\1", value)


def expand_days(value):
    tokens = re.findall(r"\b(?:sun(?:day)?|mon(?:day)?|tues?(?:day)?|wed(?:nesday)?|thurs?(?:day)?|fri(?:day)?|sat(?:urday)?)\b", value)
    indexes = [DAY_INDEX[token] for token in tokens]
    if len(indexes) >= 2 and re.search(r"[-–—]", value):
        return [DAYS[index] for index in range(indexes[0], indexes[1] + 1)]
    return [DAYS[index] for index in indexes]


def get_hours_blocks(soup):
    blocks = soup.select(".sqs-html-content")
    heading_index = next(
        (
            index
            for index, block in enumerate(blocks)
            if normalize_text(block.get_text(" ", strip=True)) == "hours of operation"
        ),
        None,
    )
    if heading_index is None:
        raise ValueError("Could not find footer Hours of Operation heading")

    labels = next(
        (block for block in blocks[heading_index + 1:] if "skiing hours" in normalize_text(block.get_text(" ", strip=True))),
        None,
    )
    times = next(
        (block for block in blocks[heading_index + 1:] if re.search(r"\d{1,2}:\d{2}\s*(?:am|pm)", normalize_text(block.get_text(" ", strip=True)))),
        None,
    )
    if not labels or not times:
        raise ValueError("Could not find footer operating hours values")
    return list(labels.stripped_strings), list(times.stripped_strings)


def get_hours():
    response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    labels, time_values = get_hours_blocks(soup)
    hours = {}
    time_index = 0
    for label in labels:
        normalized_label = normalize_text(label)
        if normalized_label == "monday":
            if time_index >= len(time_values):
                raise ValueError("Missing footer Monday time")
            hours["monday"] = normalize_time(time_values[time_index])
            time_index += 1
            continue
        if "hours" not in normalized_label:
            continue
        if time_index >= len(time_values):
            raise ValueError("Missing footer operating time")
        value = normalize_time(time_values[time_index])
        time_index += 1
        if "skiing hours" in normalized_label:
            for day in expand_days(normalized_label):
                hours[day] = value

    missing = set(DAYS) - hours.keys()
    if missing:
        raise ValueError(f"Missing Mount Jamieson hours weekdays: {sorted(missing)}")
    return {day: hours[day] for day in DAYS}


def main():
    payload = {"hours": get_hours(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
