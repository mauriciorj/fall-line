import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.greatersudbury.ca/play/ski-hills/lively-ski-hill/"
RESORT_ID = "lively-ski-hill"
DAYS = ("sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday")
HEADERS = {"User-Agent": "Mozilla/5.0"}


def normalize_text(value):
    return " ".join(value.replace("\xa0", " ").split()).lower()


def get_page_config(soup):
    config = next((script.string or script.get_text() for script in soup.find_all("script") if "contentid:" in (script.string or script.get_text())), "")
    values = {
        name: re.search(rf'{name}:"([^"]+)"', config)
        for name in ("siteid", "contentid", "contenthistid")
    }
    if any(match is None for match in values.values()):
        raise ValueError("Could not find Mura page configuration")
    return {name: match.group(1) for name, match in values.items()}


def get_hours_html():
    response = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    page = BeautifulSoup(response.content, "html.parser")
    tabs = page.select_one('div[data-object="tabs"]')
    if not tabs:
        raise ValueError("Could not find the Hours tab object")

    params = {
        "method": "processAsyncObject",
        "object": tabs.get("data-object"),
        "objectid": tabs.get("data-objectid"),
        "instanceid": tabs.get("data-instanceid"),
        "async": tabs.get("data-async"),
        "render": tabs.get("data-render"),
        **get_page_config(page),
    }
    api_url = f"{SOURCE_URL.split('/play/')[0]}/index.cfm/_api/json/v1/"
    tabs_response = requests.get(api_url, params=params, headers=HEADERS, timeout=30)
    tabs_response.raise_for_status()
    tabs_html = tabs_response.json().get("data", {}).get("html")
    if not tabs_html:
        raise ValueError("Could not load the Hours tab HTML")
    return BeautifulSoup(tabs_html, "html.parser")


def get_hours():
    soup = get_hours_html()
    hours_link = next((link for link in soup.select('[role="tab"]') if normalize_text(link.get_text()) == "hours"), None)
    if not hours_link or not hours_link.get("href", "").startswith("#"):
        raise ValueError("Could not find the Hours tab")
    panel = soup.select_one(hours_link["href"])
    if not panel:
        raise ValueError("Could not find the Hours tab content")

    hours = {}
    for paragraph in panel.find_all("p"):
        days = re.findall(r"\b(" + "|".join(DAYS) + r")s?\b", normalize_text(paragraph.get_text(" ", strip=True)))
        list_element = paragraph.find_next_sibling("ul")
        if not days or not list_element:
            continue
        value = normalize_text(list_element.find("li").get_text(" ", strip=True))
        value = value.replace("p.m.", "pm").replace("a.m.", "am")
        value = re.sub(r"\s+(am|pm)\b", r"\1", value)
        for day in days:
            hours[day] = value

    missing = set(DAYS) - hours.keys()
    if missing:
        raise ValueError(f"Missing weekday hours: {sorted(missing)}")
    return {day: hours[day] for day in DAYS}


def main():
    payload = {"hours": get_hours(), "resortId": RESORT_ID, "sourceUrl": SOURCE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
