import json
import os
import re

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

RESORT_INFO_URL = "https://www.skiresort.com/en/ski-resort/sunridge/"
TRACKS_INFO_URL = "https://www.skiresort.com/en/ski-resort/sunridge/slope-offering/"
OUTPUT_FILE = "skiresort.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}


def fetch_page_text(url):
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    return soup.get_text(" ", strip=True)


def parse_elevation(text):
    match = re.search(
        r"Elevation info\s+([0-9]+(?:[.,][0-9]+)?\s*m\s*[-–]\s*[0-9]+(?:[.,][0-9]+)?\s*m)\s*"
        r"\(Difference\s*([0-9]+(?:[.,][0-9]+)?\s*m)\)",
        text,
        re.IGNORECASE,
    )
    if not match:
        raise ValueError("Could not find elevation information")

    elevation = re.sub(r"\s+", " ", match.group(1)).strip()
    elevation = re.sub(r"\s*[-–]\s*", " - ", elevation)
    height = re.sub(r"\s*m\b", "m", match.group(2), flags=re.IGNORECASE)
    return elevation, height


def normalize_kilometers(value):
    value = re.sub(r"\s+", " ", value).strip()
    return re.sub(r"\s*km\b", "km", value, flags=re.IGNORECASE)


def parse_slope_row(text, difficulty):
    match = re.search(
        rf"\b{difficulty}\s+([0-9]+(?:[.,][0-9]+)?\s*km)\s*"
        r"\(\s*([0-9]+(?:[.,][0-9]+)?)\s*%\s*\)",
        text,
        re.IGNORECASE,
    )
    if not match:
        raise ValueError(f"Could not find {difficulty.lower()} slope information")
    return normalize_kilometers(match.group(1)), match.group(2)


def parse_slopes(text):
    section_match = re.search(
        r"(?:Runs/slopes|Ski slopes)\s+(.*?)(?=Additional(?: runs)?\b|Worth knowing\b|Longest run\b)",
        text,
        re.IGNORECASE,
    )
    if not section_match:
        raise ValueError("Could not find ski slope information")

    section = section_match.group(1)
    result = {}
    for difficulty, field_name in (
        ("Easy", "green"),
        ("Intermediate", "blue"),
        ("Difficult", "black"),
    ):
        length, proportion = parse_slope_row(section, difficulty)
        result[f"tracks-{field_name}-length"] = length
        result[f"tracks-{field_name}-proportion"] = proportion

    total_match = re.search(
        r"\bTotal\s*: ?\s*([0-9]+(?:[.,][0-9]+)?\s*km)",
        section,
        re.IGNORECASE,
    )
    if not total_match:
        raise ValueError("Could not find total slope length")
    result["tracks-total-length"] = normalize_kilometers(total_match.group(1))
    return result


def get_ski_resort_info():
    elevation, height = parse_elevation(fetch_page_text(RESORT_INFO_URL))
    result = {"elevation": elevation, "height": height}
    result.update(parse_slopes(fetch_page_text(TRACKS_INFO_URL)))
    return result


def main():
    data = get_ski_resort_info()
    output_file = os.path.join(os.path.dirname(__file__), OUTPUT_FILE)
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(data, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
