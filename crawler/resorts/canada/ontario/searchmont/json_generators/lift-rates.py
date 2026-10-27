import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

SOURCE_URL = "https://searchmont.com/"
PAGE_URL = "https://searchmont.com/lift-tickets/"
RESORT_ID = "searchmont"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


def normalize_text(value):
    return " ".join(value.replace("\xa0", " ").split()).lower()


def parse_price(value):
    match = re.search(r"\$\s*([0-9]+(?:[.,][0-9]+)?)", value)
    if not match:
        raise ValueError(f"Could not parse lift ticket price: {value}")
    amount = float(match.group(1).replace(",", "."))
    return f"${int(amount) if amount.is_integer() else amount:g}"


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

    text = normalize_text(BeautifulSoup(response.content, "html.parser").get_text(" ", strip=True))
    day_start = text.find("day tickets")
    night_start = text.find("night lift ticket")
    if day_start == -1 or night_start == -1 or night_start <= day_start:
        raise ValueError("Could not find DAY Tickets and night lift TICKET sections")
    day_section = text[day_start:night_start]
    night_section = text[night_start:]

    weekday_match = re.search(r"weekdays.*?(\$\s*[0-9]+(?:[.,][0-9]+)?)", day_section)
    weekend_match = re.search(r"weekend.*?(\$\s*[0-9]+(?:[.,][0-9]+)?)", day_section)
    night_match = re.search(r"friday & saturday.*?(\$\s*[0-9]+(?:[.,][0-9]+)?)", night_section)
    if not weekday_match or not weekend_match or not night_match:
        raise ValueError("Missing weekday, weekend, or night lift ticket price")

    weekday = parse_price(weekday_match.group(1))
    weekend = parse_price(weekend_match.group(1))
    night = parse_price(night_match.group(1))
    return {
        "day-week": {"adults": weekday},
        "day-weekend": {"adults": weekend},
        "night-week": {"adults": night},
        "night-weekend": {"adults": night},
    }


def main():
    payload = {"rates": get_lift_rates(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "lift-rates.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
