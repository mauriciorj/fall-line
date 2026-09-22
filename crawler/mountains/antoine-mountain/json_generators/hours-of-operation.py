import json
import os
import re
import time
from bs4 import NavigableString

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://antoinemountain.ca/"
PAGE_URL = "https://antoinemountain.ca/pages/hours-of-operation"
RESORT_ID = "antoine-mountain"
DAYS = ("sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday")
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


def normalize_text(value):
    return " ".join(value.lower().split())


def get_hours():
    response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    page_text = normalize_text(soup.get_text(" ", strip=True))
    if "closed for the season" in page_text:
        return {day: "closed" for day in DAYS}

    chair_heading = next(
        (
            heading
            for heading in soup.find_all(["h2", "h3", "h4"])
            if normalize_text(heading.get_text(" ", strip=True)) == "chair lift"
        ),
        None,
    )
    if not chair_heading:
        raise ValueError("Could not find Chair Lift section")
    paragraph = chair_heading.find_next("p")
    if not paragraph:
        raise ValueError("Could not find Chair Lift hours")
    time_element = paragraph.find("span")
    if not time_element:
        raise ValueError("Could not find Chair Lift time value")
    day_label = " ".join(
        text.strip() for text in paragraph.contents
        if isinstance(text, NavigableString) and text.strip()
    )
    time_value = normalize_text(time_element.get_text(" ", strip=True))
    time_value = re.sub(r"\s*[-–]\s*", " to ", time_value)
    if "friday" not in day_label.lower() or "sunday" not in day_label.lower():
        raise ValueError(f"Unsupported Chair Lift day range: {day_label}")
    return {
        "sunday": time_value,
        "monday": "closed",
        "tuesday": "closed",
        "wednesday": "closed",
        "thursday": "closed",
        "friday": time_value,
        "saturday": time_value,
    }


def main():
    payload = {"hours": get_hours(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
