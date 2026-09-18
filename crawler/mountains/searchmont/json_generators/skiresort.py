import json
import os
import re

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://searchmont.com/"
RESORT_INFO_URL = "https://www.skiresort.com/en/ski-resort/searchmont/"
TRACKS_INFO_URL = "https://www.skiresort.com/en/ski-resort/searchmont/slope-offering/"
OUTPUT_FILE = "skiresort.json"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


def fetch_page_text(url):
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser").get_text(" ", strip=True)


def parse_elevation(text):
    match = re.search(r"Elevation info\s+([0-9]+(?:[.,][0-9]+)?\s*m\s*[-–]\s*[0-9]+(?:[.,][0-9]+)?\s*m)\s*\(Difference\s*([0-9]+(?:[.,][0-9]+)?\s*m)\)", text, re.IGNORECASE)
    if not match:
        raise ValueError("Could not find elevation information")
    elevation = re.sub(r"\s*[-–]\s*", " - ", re.sub(r"\s+", " ", match.group(1)).strip())
    height = re.sub(r"\s*m\b", "m", match.group(2), flags=re.IGNORECASE)
    return elevation, height


def normalize_kilometers(value):
    return re.sub(r"\s*km\b", "km", re.sub(r"\s+", " ", value).strip(), flags=re.IGNORECASE)


def parse_slope_row(text, difficulty):
    match = re.search(rf"\b{difficulty}\s+([0-9]+(?:[.,][0-9]+)?\s*km)\s*(?:\(\s*([0-9]+(?:[.,][0-9]+)?)\s*%\s*\))?", text, re.IGNORECASE)
    if not match:
        raise ValueError(f"Could not find {difficulty.lower()} slope information")
    return normalize_kilometers(match.group(1)), match.group(2) or "0"


def parse_slopes(text):
    section = re.search(r"(?:Runs/slopes|Ski slopes)\s+(.*?)(?=Additional(?: runs)?\b|Worth knowing\b|Longest run\b)", text, re.IGNORECASE)
    if not section:
        raise ValueError("Could not find ski slope information")
    result = {}
    for difficulty, field in (("Easy", "green"), ("Intermediate", "blue"), ("Difficult", "black")):
        length, proportion = parse_slope_row(section.group(1), difficulty)
        result[f"tracks-{field}-length"] = length
        result[f"tracks-{field}-proportion"] = proportion
    total = re.search(r"\bTotal\s*:?\s*([0-9]+(?:[.,][0-9]+)?\s*km)", section.group(1), re.IGNORECASE)
    if not total:
        raise ValueError("Could not find total slope length")
    result["tracks-total-length"] = normalize_kilometers(total.group(1))
    return result


def get_ski_resort_info():
    elevation, height = parse_elevation(fetch_page_text(RESORT_INFO_URL))
    result = {"elevation": elevation, "height": height}
    result.update(parse_slopes(fetch_page_text(TRACKS_INFO_URL)))
    return result


def main():
    output_file = os.path.join(os.path.dirname(__file__), OUTPUT_FILE)
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(get_ski_resort_info(), output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
