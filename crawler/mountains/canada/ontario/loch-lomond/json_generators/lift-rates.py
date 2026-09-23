import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup, NavigableString
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

SOURCE_URL = "https://www.lochlomond.ca/"
PAGE_URL = "https://www.lochlomond.ca/lift-tickets/"
RESORT_ID = "loch-lomond"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}
CATEGORIES = (("adult", "adults"), ("senior", "seniors"), ("youth", "youth"))


def normalize_text(value):
    return " ".join(value.replace("\xa0", " ").split())


def get_season_prices_text(soup):
    heading = next(
        (
            element
            for element in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
            if normalize_text(element.get_text(" ", strip=True)).lower() == "2025-26 season prices"
        ),
        None,
    )
    if not heading:
        raise ValueError("Could not find 2025-26 Season Prices section")

    level = int(heading.name[1])
    content = []
    for node in heading.next_elements:
        if getattr(node, "name", None) and re.fullmatch(r"h[1-6]", node.name) and int(node.name[1]) <= level:
            break
        if isinstance(node, NavigableString):
            content.append(str(node))
    return normalize_text(" ".join(content))


def get_lift_rates():
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=(502, 503, 504),
        allowed_methods=frozenset({"GET"}),
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    try:
        response = session.get(PAGE_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
    except requests.HTTPError as error:
        if error.response is None or error.response.status_code not in (403, 502, 503, 504):
            raise
        with open(os.path.join(os.path.dirname(__file__), "lift-rates.json"), encoding="utf-8") as source:
            fallback = json.load(source).get("rates")
        if isinstance(fallback, dict):
            return fallback
        raise

    soup = BeautifulSoup(response.content, "html.parser")
    text = get_season_prices_text(soup)
    rates = {}
    for category, key in CATEGORIES:
        match = re.search(rf"\b{category}\b.*?online\s*:\s*(\$?\s*[\d,.]+)", text, re.IGNORECASE)
        if not match:
            raise ValueError(f"Could not find online {category} lift ticket price")
        rates[key] = normalize_text(match.group(1)).replace(" ", "")
    return {"day-week": rates.copy(), "day-weekend": rates.copy()}


def main():
    payload = {"rates": get_lift_rates(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "lift-rates.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
