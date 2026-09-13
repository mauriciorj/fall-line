"""Snow Valley rental rates crawler."""

import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

URL = "https://www.skisnowvalley.com/plan/ski-snowboard/equipment-rentals/"
RESORT_ID = "snow-valley-ski-resort"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
}


def parse_price(value):
    if value in (None, ""):
        return None
    match = re.search(r"\$?\s*(\d+(?:[.,]\d+)?)", str(value))
    if not match:
        return None
    amount = float(match.group(1).replace(",", "."))
    return f"${int(amount) if amount.is_integer() else amount:g}"


def parse_price_list(widget):
    items = []
    for element in widget.find_all("li"):
        title = element.find("span", class_="elementor-price-list-title")
        price = element.find("span", class_="elementor-price-list-price")
        description = element.find("p", class_="elementor-price-list-description")
        items.append(
            {
                "name": title.get_text(strip=True) if title else "",
                "price": price.get_text(strip=True) if price else "",
                "description": description.get_text(" ", strip=True)
                if description
                else "",
            }
        )
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


def normalize_rentals(sections):
    result = {"ski": {}, "snowboard": {}, "items": {}}
    for section in sections:
        title = section.get("title", "").lower()
        items = section.get("items", [])
        if "full day ski" not in title or "board" not in title:
            continue
        for item in items:
            name = item.get("name", "").lower()
            price = parse_price(item.get("price"))
            if price is None:
                continue
            if "adult" in name:
                result["ski"]["adults"] = price
                result["snowboard"]["adults"] = price
            elif "youth" in name or "senior" in name or "6-17" in name:
                result["ski"]["youth"] = price
                result["snowboard"]["youth"] = price

    for section in sections:
        title = section.get("title", "").lower()
        if "a la carte ski or board rental" not in title:
            continue
        for item in section.get("items", []):
            name = item.get("name", "").lower()
            price = parse_price(item.get("price"))
            if price is None:
                continue
            if "adult" in name and "ski" not in name and "board" not in name:
                result["items"]["skis"] = price
                result["items"]["snowboard"] = price
            elif "helmet" in name:
                result["items"]["helmet"] = price

    for section in sections:
        title = section.get("title", "").lower()
        if "a la carte ski or board boot rental" not in title:
            continue
        for item in section.get("items", []):
            if "adult" not in item.get("name", "").lower():
                continue
            price = parse_price(item.get("price"))
            if price is not None:
                result["items"]["boots"] = price

    missing = [
        f"{section}.{age_group}"
        for section in ("ski", "snowboard")
        for age_group in ("youth", "adults")
        if age_group not in result[section]
    ]
    if missing:
        print(f"Missing rental values: {', '.join(missing)}")
        return None
    return result


def main():
    rentals = normalize_rentals(get_rentals())
    if rentals is None:
        return
    payload = {
        "rentals": rentals,
        "resortId": RESORT_ID,
        "sourceUrl": URL,
        "updatedAt": int(time.time() * 1000),
    }
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
