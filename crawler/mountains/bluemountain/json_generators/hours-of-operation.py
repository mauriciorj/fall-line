import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

from dtos import to_hours

URL = "https://www.bluemountain.ca/mountain/hours"
RESORT_ID = "blue-mountain"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}
DAY_PATTERN = re.compile(
    r"^(DAILY|MON\.?|TUES?\.?|WED\.?|THURS?\.?|FRI\.?|SAT\.?|SUN\.?|"
    r"MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY)"
    r"(\s*[-&]\s*.+)?\.?$",
    re.I,
)
TIME_PATTERN = re.compile(r"\d+[:\d]*\s*(AM|PM)|CLOSED", re.I)


def clean_text(text):
    return re.sub(r"\s+", " ", text or "").strip()


def extract_hours_from_page_text(soup):
    lines = [
        line.strip()
        for line in soup.get_text(separator="\n", strip=True).split("\n")
        if line.strip()
    ]
    result = {}
    section = None
    item = None
    period = None
    index = 0

    while index < len(lines):
        line = lines[index]
        if re.match(r"^(ATTRACTIONS|GUEST SERVICES|LODGING|DINING|SHOPPING|RENTALS)", line, re.I):
            section = line.title()
            result.setdefault(section, {})
            item = None
            period = None
            index += 1
            continue
        if re.match(r"^(As Of .+|[A-Z][a-z]{2,3}\.\s*\d+\s*-\s*.+)$", line):
            period = line
            index += 1
            continue
        if DAY_PATTERN.match(line) and index + 1 < len(lines) and TIME_PATTERN.search(lines[index + 1]):
            if section and item:
                target = result[section].setdefault(item, {})
                if period:
                    target = target.setdefault(period, {})
                target[line] = clean_text(lines[index + 1])
            index += 2
            continue
        if (
            section
            and len(line) < 60
            and not DAY_PATTERN.match(line)
            and not TIME_PATTERN.search(line)
            and index + 1 < len(lines)
            and (DAY_PATTERN.match(lines[index + 1]) or lines[index + 1].startswith("As Of"))
        ):
            item = clean_text(line)
            period = None
        index += 1

    return result


def get_hours():
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return extract_hours_from_page_text(BeautifulSoup(response.content, "html.parser"))


def main():
    payload = {
        "hours": to_hours(get_hours()),
        "resortId": RESORT_ID,
        "sourceUrl": URL,
        "updatedAt": int(time.time() * 1000),
    }
    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
