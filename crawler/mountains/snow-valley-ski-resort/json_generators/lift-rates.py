"""Snow Valley lift rates crawler."""

import json
import os
import re
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

URL = "https://www.skisnowvalley.com/plan/ski-snowboard/tickets-and-passes/"
RESORT_ID = "snow-valley-ski-resort"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
}
RATE_KEYS = ("night-week", "night-weekend", "day-week", "day-weekend")
AGE_GROUPS = ("youth", "adults", "seniors")


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
                    categories.append(
                        {"category": current_category or title, "items": items}
                    )
        if not categories:
            continue
        result["Season Passes" if "pass" in title.lower() else "Lift Tickets"].append(
            {"title": title, "subtitle": subtitle, "categories": categories}
        )
    return result


def parse_price_pair(value):
    prices = re.findall(r"\$?\s*(\d+(?:[.,]\d+)?)", str(value))
    if not prices:
        return None
    parsed = [f"${float(price.replace(',', '.')):g}" for price in prices[:2]]
    if len(parsed) == 1:
        parsed.append(parsed[0])
    return parsed


def category_age_groups(category):
    normalized = category.lower()
    if "adult" in normalized:
        return ("adults",)
    if "youth" in normalized and "senior" in normalized:
        return ("youth", "seniors")
    return ()


def normalize_lift_rates(rates):
    normalized = {rate_key: {} for rate_key in RATE_KEYS}
    for section in rates.get("Lift Tickets", []):
        source_text = f"{section.get('title', '')} {section.get('subtitle', '')}".lower()
        if "buy now" not in source_text and "online" not in source_text:
            continue
        for category in section.get("categories", []):
            age_groups = category_age_groups(category.get("category", ""))
            if not age_groups:
                continue
            for item in category.get("items", []):
                item_name = item.get("name", "").lower()
                prices = parse_price_pair(item.get("price", ""))
                if not prices:
                    continue
                if "6 hour lift" in item_name:
                    rate_keys = ("day-week", "day-weekend")
                elif "all night lift" in item_name:
                    rate_keys = ("night-week", "night-weekend")
                else:
                    continue
                for age_group in age_groups:
                    normalized[rate_keys[0]][age_group] = prices[0]
                    normalized[rate_keys[1]][age_group] = prices[1]

    missing = [
        f"{rate_key}.{age_group}"
        for rate_key in RATE_KEYS
        for age_group in AGE_GROUPS
        if age_group not in normalized[rate_key]
    ]
    if missing:
        print(f"Missing lift-rate values: {', '.join(missing)}")
        return None
    return normalized


def main():
    rates = normalize_lift_rates(get_rates())
    if rates is None:
        return
    payload = {
        "rates": rates,
        "resortId": RESORT_ID,
        "sourceUrl": URL,
        "updatedAt": int(time.time() * 1000),
    }
    output_file = os.path.join(os.path.dirname(__file__), "lift-rates.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
