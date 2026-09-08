"""
Chicopee hours crawler.
Scrapes hours from https://www.discoverchicopee.com/contact#hours.
"""

import json
import os
import re
import sys
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dtos import to_hours

URL = "https://www.discoverchicopee.com/contact#hours"
RESORT_ID = "chicopee"
DAY_KEYWORDS = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
    "Daily",
    "Weekday",
    "Weekend",
)


def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(service=Service(), options=options)


def _is_day_line(line):
    return any(line.lower().startswith(day.lower()) for day in DAY_KEYWORDS)


def _clean_lines(element):
    return [
        line
        for line in element.get_text(separator="\n", strip=True).split("\n")
        if line and line.lower() not in {"clock icon", "hours of operation"}
    ]


def _parse_section(lines):
    hours = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        if not _is_day_line(line):
            index += 1
            continue
        day, separator, value = line.partition(":")
        day = day.strip()
        if separator and value.strip():
            hours[day] = value.strip()
            index += 1
        elif index + 1 < len(lines) and not _is_day_line(lines[index + 1]):
            hours[day] = lines[index + 1]
            index += 2
        else:
            index += 1
    if not hours and lines:
        hours["Daily"] = " ".join(lines)
    return hours


def extract_hours_section(soup):
    heading = next(
        (
            candidate
            for candidate in soup.find_all(["h2", "h3"])
            if "hours of operation" in candidate.get_text(" ", strip=True).lower()
        ),
        None,
    )
    if not heading:
        return {}

    parent = heading.find_parent(["section", "div"]) or heading.parent
    result = {}
    for section_heading in parent.find_all("h3"):
        section_name = section_heading.get_text(" ", strip=True)
        if not section_name or section_name.lower() == "hours of operation":
            continue
        lines = []
        sibling = section_heading.find_next_sibling()
        while sibling and sibling.name != "h3":
            lines.extend(_clean_lines(sibling))
            sibling = sibling.find_next_sibling()
        section_hours = _parse_section(lines)
        if section_hours:
            result[section_name] = section_hours
    return result


def get_hours():
    print(f"Fetching {URL}...")
    driver = get_driver()
    try:
        driver.get(URL)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        return extract_hours_section(BeautifulSoup(driver.page_source, "html.parser"))
    finally:
        driver.quit()


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
