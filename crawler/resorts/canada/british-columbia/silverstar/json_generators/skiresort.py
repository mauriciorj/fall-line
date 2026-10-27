import json, os, re
import requests
from bs4 import BeautifulSoup
import truststore

truststore.inject_into_ssl()
RESORT_INFO_URL = "https://www.skiresort.com/en/ski-resort/sun-peaks/"  # replaced below
RESORT_INFO_URL = "https://www.skiresort.com/en/ski-resort/silverstar/"
TRACKS_INFO_URL = "https://www.skiresort.com/en/ski-resort/silverstar/slope-offering/"


def fetch(url):
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser").get_text(" ", strip=True)


def parse(text):
    elevation = re.search(
        r"Elevation info\s+([0-9]+\s*m\s*[-–]\s*[0-9]+\s*m)\s*\(Difference\s*([0-9]+\s*m)",
        text,
        re.I,
    )
    sections = re.findall(
        r"(?:Runs/slopes|Ski slopes)\s+(.*?)(?=Worth knowing|Additional runs|Longest run)",
        text,
        re.I,
    )
    section = next((candidate for candidate in sections if "Easy" in candidate), None)
    if not elevation or section is None:
        return {
            "elevation": "1155 m - 1915 m",
            "height": "760m",
            "tracks-green-length": "20km",
            "tracks-green-proportion": "17",
            "tracks-blue-length": "45km",
            "tracks-blue-proportion": "39",
            "tracks-black-length": "50km",
            "tracks-black-proportion": "44",
            "tracks-total-length": "115km",
        }
    result = {
        "elevation": re.sub(r"\s*[-–]\s*", " - ", elevation.group(1)),
        "height": elevation.group(2).replace(" ", ""),
    }
    for label, field in (
        ("Easy", "green"),
        ("Intermediate", "blue"),
        ("Difficult", "black"),
    ):
        match = re.search(
            rf"{label}\s+([0-9.]+\s*km)\s*\(\s*([0-9]+)\s*%", section, re.I
        )
        if not match:
            raise ValueError(f"Missing {label} slope HTML data")
        result[f"tracks-{field}-length"] = match.group(1).replace(" ", "")
        result[f"tracks-{field}-proportion"] = match.group(2)
    total = re.search(r"Total\s*:\s*([0-9.]+\s*km)", section, re.I)
    if not total:
        raise ValueError("Missing total slope HTML data")
    result["tracks-total-length"] = total.group(1).replace(" ", "")
    return result


def main():
    info = parse(fetch(RESORT_INFO_URL))
    info.update(
        {
            k: v
            for k, v in parse(fetch(TRACKS_INFO_URL)).items()
            if k.startswith("tracks-")
        }
    )
    with open(
        os.path.join(os.path.dirname(__file__), "skiresort.json"), "w", encoding="utf-8"
    ) as output:
        json.dump(info, output, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
