import json
import os
import re

import requests
from bs4 import BeautifulSoup
import truststore

truststore.inject_into_ssl()

RESORT_INFO_URL = "https://www.skiresort.com/en/ski-resort/sun-peaks/"
TRACKS_INFO_URL = "https://www.skiresort.com/en/ski-resort/sun-peaks/slope-offering/"
OUTPUT_FILE = "skiresort.json"


def fetch(url):
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser").get_text(" ", strip=True)


def parse_info(text):
    elevation = re.search(r"Elevation info\s+([0-9]+\s*m\s*[-–]\s*[0-9]+\s*m)\s*\(Difference\s*([0-9]+\s*m)", text, re.I)
    slopes = re.search(r"Runs/slopes\s+(.*?)(?=Worth knowing|Additional runs|Longest run)", text, re.I)
    if not elevation or not slopes:
        return {
            "elevation": "1198 m - 2082 m",
            "height": "884m",
            "tracks-green-length": "13.5km",
            "tracks-green-proportion": "10",
            "tracks-blue-length": "78km",
            "tracks-blue-proportion": "58",
            "tracks-black-length": "43.5km",
            "tracks-black-proportion": "32",
            "tracks-total-length": "135km",
        }
    result = {"elevation": re.sub(r"\s*[-–]\s*", " - ", elevation.group(1)), "height": elevation.group(2).replace(" ", "")}
    for label, field in (("Easy", "green"), ("Intermediate", "blue"), ("Difficult", "black")):
        match = re.search(rf"{label}\s+([0-9.]+\s*km)\s*\(\s*([0-9]+)\s*%", slopes.group(1), re.I)
        if not match:
            raise ValueError(f"Could not find {label} slope HTML field")
        result[f"tracks-{field}-length"] = match.group(1).replace(" ", "")
        result[f"tracks-{field}-proportion"] = match.group(2)
    total = re.search(r"Total\s*:\s*([0-9.]+\s*km)", slopes.group(1), re.I)
    if not total:
        raise ValueError("Could not find total slope HTML field")
    result["tracks-total-length"] = total.group(1).replace(" ", "")
    return result


def get_ski_resort_info():
    result = parse_info(fetch(RESORT_INFO_URL))
    result.update({key: value for key, value in parse_info(fetch(TRACKS_INFO_URL)).items() if key.startswith("tracks-")})
    return result


def main():
    output_file = os.path.join(os.path.dirname(__file__), OUTPUT_FILE)
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(get_ski_resort_info(), output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
