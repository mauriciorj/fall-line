"""Snow Valley rental rates crawler."""

import json
import os
import sys
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dtos import to_rentals_dto

URL = "https://www.skisnowvalley.com/plan/ski-snowboard/equipment-rentals/"
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


def get_rentals():
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    result = []
    for container in soup.find_all("div", class_="e-child"):
        if len(container.find_all("ul", class_="elementor-price-list")) != 1:
            continue
        title = ""
        subtitle = ""
        items = []
        for widget in container.find_all("div", class_="elementor-widget"):
            widget_type = widget.get("data-widget_type", "")
            if "heading" in widget_type:
                heading = widget.find(class_="elementor-heading-title")
                text = heading.get_text(strip=True) if heading else ""
                if not title:
                    title = text
                elif not subtitle:
                    subtitle = text
            elif "price-list" in widget_type:
                items = parse_price_list(widget)
        if items:
            section = {"title": title, "items": items}
            if subtitle:
                section["subtitle"] = subtitle
            result.append(section)
    return result


def main():
    payload = {"rentals": to_rentals_dto(get_rentals()), "resortId": RESORT_ID, "sourceUrl": URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
