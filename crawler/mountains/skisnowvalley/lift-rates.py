import json
import os
import sys
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from convex_client import push_resort_rates

URL = "https://www.skisnowvalley.com/plan/ski-snowboard/tickets-and-passes/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
RESORT_ID = "snow-valley-ski-resort"
RESORT_NAME = "Ski Snow Valley"


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


def parse_ticket_section(container):
    """Parse a ticket section container with headings and price lists."""
    widgets = container.find_all("div", class_="elementor-widget")
    section = {"title": "", "subtitle": "", "categories": []}
    current_category = None

    for w in widgets:
        wtype = w.get("data-widget_type", "")
        if "heading" in wtype:
            heading = w.find(class_="elementor-heading-title")
            text = heading.get_text(strip=True) if heading else ""
            if not section["title"]:
                section["title"] = text
            elif not section["subtitle"]:
                section["subtitle"] = text
            else:
                current_category = text
        elif "price-list" in wtype:
            items = parse_price_list(w)
            if items:
                section["categories"].append({
                    "category": current_category or section["title"],
                    "items": items,
                })

    return section


def get_rates():
    """Fetch and parse all ticket and pass rates from Ski Snow Valley."""
    print(f"Fetching {URL}...")
    response = requests.get(URL, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    containers = soup.find_all("div", class_="e-child")

    result = {"Lift Tickets": [], "Season Passes": []}

    for c in containers:
        price_lists = c.find_all("ul", class_="elementor-price-list")
        if not price_lists:
            continue

        section = parse_ticket_section(c)
        title = section["title"].lower()

        if "pass" in title:
            result["Season Passes"].append(section)
        elif "rate" in title or "buy" in title:
            result["Lift Tickets"].append(section)

    return result


def main():
    rates = get_rates()
    output_file = os.path.join(os.path.dirname(__file__), "lift-rates.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(rates, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")

    result = push_resort_rates(
        RESORT_ID,
        RESORT_NAME,
        URL,
        rates,
        fetched_at_ms=int(time.time() * 1000),
    )
    if result is not None:
        print("Pushed to Convex:", result)


if __name__ == "__main__":
    main()
