import json
import os
import sys
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from convex_client import push_resort_rentals

URL = "https://www.skisnowvalley.com/plan/ski-snowboard/equipment-rentals/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
RESORT_ID = "snow-valley-ski-resort"


def parse_price_list(widget):
    """Parse an Elementor price-list widget into a list of items."""
    items = []
    for li in widget.find_all("li"):
        title = li.find("span", class_="elementor-price-list-title")
        price = li.find("span", class_="elementor-price-list-price")
        desc = li.find("p", class_="elementor-price-list-description")
        items.append({
            "name": title.get_text(strip=True) if title else "",
            "price": price.get_text(strip=True) if price else "",
            "description": desc.get_text(separator=" ", strip=True) if desc else "",
        })
    return items


def parse_rental_section(container):
    """Parse a rental section container with headings and a price list."""
    widgets = container.find_all("div", class_="elementor-widget")
    title = ""
    subtitle = ""
    items = []

    for w in widgets:
        wtype = w.get("data-widget_type", "")
        if "heading" in wtype:
            heading = w.find(class_="elementor-heading-title")
            text = heading.get_text(strip=True) if heading else ""
            if not title:
                title = text
            elif not subtitle:
                subtitle = text
        elif "price-list" in wtype:
            items = parse_price_list(w)

    section = {"title": title, "items": items}
    if subtitle:
        section["subtitle"] = subtitle
    return section


def get_rentals():
    """Fetch and parse all rental prices from Ski Snow Valley."""
    print(f"Fetching {URL}...")
    response = requests.get(URL, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    containers = soup.find_all("div", class_="e-child")

    result = []

    for c in containers:
        price_lists = c.find_all("ul", class_="elementor-price-list")
        # Skip containers with no price lists or multiple (aggregated parent)
        if len(price_lists) != 1:
            continue

        section = parse_rental_section(c)
        if not section["items"]:
            continue

        result.append(section)

    return result


def main():
    rentals = get_rentals()
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(rentals, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")

    result = push_resort_rentals(
        RESORT_ID,
        URL,
        rentals,
        updated_at_ms=int(time.time() * 1000),
    )
    if result is not None:
        print("Pushed to Convex:", result)


if __name__ == "__main__":
    main()
