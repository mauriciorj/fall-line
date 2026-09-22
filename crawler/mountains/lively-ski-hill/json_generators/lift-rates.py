import json
import os
import re
import time
from urllib.parse import urlsplit, urlunsplit

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

RESORT_ID = "lively-ski-hill"
SOURCE_URL = "https://www.greatersudbury.ca/play/ski-hills/lively-ski-hill/"
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


def load_async_html(page, element):
    params = {
        "method": "processAsyncObject",
        "object": element.get("data-object"),
        "objectid": element.get("data-objectid"),
        "instanceid": element.get("data-instanceid"),
        "async": element.get("data-async"),
        "render": element.get("data-render"),
        **get_page_config(page),
    }
    if element.get("data-feedname"):
        params["feedname"] = element["data-feedname"]
    parts = urlsplit(SOURCE_URL)
    api_url = urlunsplit((parts.scheme, parts.netloc, "/index.cfm/_api/json/v1/", "", ""))
    response = requests.get(api_url, params=params, headers=HEADERS, timeout=30)
    response.raise_for_status()
    html = response.json().get("data", {}).get("html")
    if not html:
        raise ValueError("Could not load async HTML")
    return BeautifulSoup(html, "html.parser")


def get_lift_ticket_table():
    response = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    page = BeautifulSoup(response.content, "html.parser")
    tabs = page.select_one('div[data-object="tabs"]')
    if not tabs:
        raise ValueError("Could not find the tabs object")

    tabs_soup = load_async_html(page, tabs)
    fees_link = next((link for link in tabs_soup.select('[role="tab"]') if normalize_text(link.get_text()) == "fees"), None)
    if not fees_link or not fees_link.get("href", "").startswith("#"):
        raise ValueError("Could not find the Fees tab")
    fees_panel = tabs_soup.select_one(fees_link["href"])
    accordion = fees_panel.select_one('[data-object="accordions"]') if fees_panel else None
    if not accordion:
        raise ValueError("Could not find the Fees accordion")

    accordion_soup = load_async_html(page, accordion)
    title = next((heading for heading in accordion_soup.select("h2.accordion-cgs-title") if normalize_text(heading.get_text()) == "lift tickets"), None)
    if not title:
        raise ValueError("Could not find the Lift Tickets section")
    section = title.find_next_sibling("div")
    heading = next((item for item in section.find_all("h3") if normalize_text(item.get_text()) == "lift ticket prices"), None)
    if not heading:
        raise ValueError("Could not find Lift Ticket Prices")
    table = heading.find_next("table")
    if not table:
        raise ValueError("Could not find the Lift Ticket Prices table")
    return table


def get_rates():
    table = get_lift_ticket_table()
    headers = [normalize_text(cell.get_text(" ", strip=True)) for cell in table.select("thead th")]
    try:
        full_day_index = headers.index("full day price")
    except ValueError as error:
        raise ValueError("Could not find Full Day Price column") from error

    rates = {}
    for row in table.select("tbody tr"):
        cells = row.find_all(["th", "td"])
        if len(cells) <= full_day_index:
            continue
        age = normalize_text(cells[0].get_text(" ", strip=True))
        price = cells[full_day_index].get_text(" ", strip=True)
        if age == "youth (15 plus) and adult":
            rates["youth"] = price
            rates["adults"] = price
        elif age == "senior (65+)":
            rates["seniors"] = price

    required = {"youth", "adults", "seniors"}
    if required - rates.keys():
        raise ValueError(f"Missing lift ticket rates: {sorted(required - rates.keys())}")
    return {"day-week": rates.copy(), "day-weekend": rates.copy()}


def main():
    payload = {"rates": get_rates(), "resortId": RESORT_ID, "sourceUrl": SOURCE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "lift-rates.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
