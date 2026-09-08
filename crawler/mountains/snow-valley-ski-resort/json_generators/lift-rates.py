"""Snow Valley lift rates crawler."""

import json
import os
import sys
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dtos import to_rates_dto

URL = "https://www.skisnowvalley.com/plan/ski-snowboard/tickets-and-passes/"
RESORT_ID = "snow-valley-ski-resort"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}


def parse_price_list(widget):
    items = []
    for element in widget.find_all("li"):
        title = element.find("span", class_="elementor-price-list-title")
        price = element.find("span", class_="elementor-price-list-price")
        description = element.find("p", class_="elementor-price-list-description")
        items.append({"name": title.get_text(strip=True) if title else "", "price": price.get_text(strip=True) if price else "", "description": description.get_text(" ", strip=True) if description else ""})
    return items


def get_rates():
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    result = {"Lift Tickets": [], "Season Passes": []}
    for container in soup.find_all("div", class_="e-child"):
        if not container.find_all("ul", class_="elementor-price-list"):
            continue
        widgets = container.find_all("div", class_="elementor-widget")
        title = ""
        subtitle = ""
        categories = []
        current_category = None
        for widget in widgets:
            widget_type = widget.get("data-widget_type", "")
            if "heading" in widget_type:
                heading = widget.find(class_="elementor-heading-title")
                text = heading.get_text(strip=True) if heading else ""
                if not title:
                    title = text
                elif not subtitle:
                    subtitle = text
                else:
                    current_category = text
            elif "price-list" in widget_type:
                items = parse_price_list(widget)
                if items:
                    categories.append({"category": current_category or title, "items": items})
        if not categories:
            continue
        result["Season Passes" if "pass" in title.lower() else "Lift Tickets"].append({"title": title, "subtitle": subtitle, "categories": categories})
    return result


def main():
    payload = {"rates": to_rates_dto(get_rates()), "resortId": RESORT_ID, "sourceUrl": URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "lift-rates.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
