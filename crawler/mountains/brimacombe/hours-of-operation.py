import json
import os
import re
import sys
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from convex_client import push_resort_hours
from dtos import to_hours

URL = "https://brimacombe.ca/contact-us/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
RESORT_ID = "brimacombe"

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def extract_hours(soup):
    """Extract hours of operation from the contact page."""
    heading = next(
        (
            candidate
            for candidate in soup.find_all(["h2", "h3", "h4"])
            if re.search(
                r"\bHOURS OF OPERATION\b",
                candidate.get_text(" ", strip=True),
                re.I,
            )
        ),
        None,
    )
    if not heading:
        return {}

    container = heading.find_parent("div")
    paragraphs = container.find_all("p") if container else []
    if not paragraphs:
        return {}

    # Split the <p> text by lines using get_text with \n separator
    lines = []
    for paragraph in paragraphs:
        text = paragraph.get_text(separator="\n", strip=False)
        lines.extend(line.strip() for line in text.split("\n") if line.strip())

    section_headers = {
        strong.get_text(" ", strip=True)
        for paragraph in paragraphs
        for strong in paragraph.find_all("strong")
        if strong.get_text(" ", strip=True)
    }

    result = {}
    current_section = None
    pending_day = None

    for line in lines:
        # Check if this is a day label (e.g. "Monday:")
        day_match = next(
            (
                day
                for day in DAYS
                if re.match(rf"^{re.escape(day)}(?:\s*:|\s*$)", line, re.I)
            ),
            None,
        )

        if day_match:
            # Day and time may be on the same line or split across two
            after_day = re.sub(
                rf"^{re.escape(day_match)}\s*:?\s*",
                "",
                line,
                flags=re.I,
            ).strip()
            if after_day:
                if current_section:
                    result.setdefault(current_section, {})[day_match] = after_day
                pending_day = None
            else:
                pending_day = day_match
        elif pending_day:
            # This line is the time for the previous day
            if current_section:
                result.setdefault(current_section, {})[pending_day] = line
            pending_day = None
        elif line in section_headers:
            # Section header line
            current_section = line
            result.setdefault(current_section, {})
            pending_day = None

    # Remove empty sections (parent titles with no day entries)
    result = {k: v for k, v in result.items() if v}

    return result


def get_hours():
    """Fetch and parse hours of operation from Brimacombe."""
    print(f"Fetching {URL}...")
    response = requests.get(URL, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    return extract_hours(soup)


def main():
    hours = get_hours()
    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(hours, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")

    result = push_resort_hours(
        RESORT_ID,
        URL,
        to_hours(hours),
        updated_at_ms=int(time.time() * 1000),
    )
    if result is not None:
        print("Pushed to Convex:", result)


if __name__ == "__main__":
    main()
