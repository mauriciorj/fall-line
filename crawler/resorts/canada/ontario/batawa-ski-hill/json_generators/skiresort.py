import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

PAGE_URL = "https://www.skiresort.com/en/ski-resort/batawa-ski-hill/"
OUTPUT_FILE = "skiresort.json"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def main():
    response = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    text = BeautifulSoup(response.content, "html.parser").get_text(" ", strip=True)
    elevation = re.search(
        r"Elevation info\s+([0-9]+ m - [0-9]+ m)\s+\(Difference\s+([0-9]+ m)\)",
        text,
        re.IGNORECASE,
    )
    slopes = re.search(
        r"Total:\s+([0-9.]+ km).*?Easy\s+([0-9.]+ km).*?\(([0-9]+) %\).*?"
        r"Intermediate\s+([0-9.]+ km).*?\(([0-9]+) %\).*?Difficult\s+([0-9.]+ km).*?\(([0-9]+) %",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if not elevation or not slopes:
        raise ValueError("Could not parse Skiresort HTML")
    data = {
        "elevation": elevation.group(1),
        "height": elevation.group(2),
        "tracks-total-length": slopes.group(1),
        "tracks-green-length": slopes.group(2),
        "tracks-green-proportion": slopes.group(3),
        "tracks-blue-length": slopes.group(4),
        "tracks-blue-proportion": slopes.group(5),
        "tracks-black-length": slopes.group(6),
        "tracks-black-proportion": slopes.group(7),
    }
    output_file = os.path.join(os.path.dirname(__file__), OUTPUT_FILE)
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(data, output, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
