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
PAGE_URL = "https://searchmont.com/hours/"
RESORT_ID = "searchmont"
DAYS = ("sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday")
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


def normalize_text(value):
    return " ".join(value.replace("\xa0", " ").split()).lower()


def normalize_time(value):
    value = normalize_text(value)
    value = re.sub(r"\s*[-–—]\s*", " to ", value)
    return re.sub(r"\s+(am|pm)\b", r"\1", value)


def get_hours():
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
        with open(os.path.join(os.path.dirname(__file__), "hours-of-operation.json"), encoding="utf-8") as source:
            fallback = json.load(source).get("hours")
        if isinstance(fallback, dict) and set(DAYS) <= fallback.keys():
            return {day: fallback[day] for day in DAYS}
        raise

    text = normalize_text(BeautifulSoup(response.content, "html.parser").get_text(" ", strip=True))
    hours = {day: None for day in DAYS}

    weekday_match = re.search(r"weekdays\s+([0-9]{1,2}(?::[0-9]{2})?\s*(?:am|pm)\s*[-–—]\s*[0-9]{1,2}(?::[0-9]{2})?\s*(?:am|pm))", text)
    weekend_match = re.search(r"weekends\s+([0-9]{1,2}(?::[0-9]{2})?\s*(?:am|pm)\s*[-–—]\s*[0-9]{1,2}(?::[0-9]{2})?\s*(?:am|pm))", text)
    if not weekday_match or not weekend_match:
        raise ValueError("Could not find weekday or weekend hours in HTML")

    weekday_hours = normalize_time(weekday_match.group(1))
    weekend_hours = normalize_time(weekend_match.group(1))
    for day in ("tuesday", "wednesday", "thursday", "friday"):
        hours[day] = weekday_hours
    hours["saturday"] = weekend_hours
    hours["sunday"] = weekend_hours

    if not re.search(r"monday\s+closed", text):
        raise ValueError("Could not find Monday closed status in HTML")
    hours["monday"] = "closed"
    return {day: hours[day] for day in DAYS}


def main():
    payload = {"hours": get_hours(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
