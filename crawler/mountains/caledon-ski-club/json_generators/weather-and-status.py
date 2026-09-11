import json
import os
import re
import sys
import time

from bs4 import BeautifulSoup, NavigableString
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dtos import to_weather_dto

URL = "https://caledonskiclub.com/private-lessons"
RESORT_ID = "caledon-ski-club"


def get_trail_status():
    print(f"Fetching {URL}...")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(URL)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")
        data = {"snow_conditions": {}, "trails": [], "lifts": []}

        snow_section = soup.select_one("#tab_popup_snow") or _find_section(
            soup, r"Snow\s*Conditions"
        )
        if snow_section:
            data["snow_conditions"] = _parse_snow_conditions(snow_section)

        trail_section = soup.select_one("#tab_popup_hill") or _find_section(
            soup, r"Trail\s*Status"
        )
        if trail_section:
            data["trails"].extend(_parse_trail_lines(trail_section))
            data["trails"].extend(
                _parse_status_list(trail_section.select_one("ul.hill_status"))
            )
            for table in trail_section.find_all("table"):
                for row in table.find_all("tr"):
                    cells = row.find_all(["td", "th"])
                    if len(cells) < 2:
                        continue
                    name = cells[0].get_text(" ", strip=True)
                    if name and name.lower() not in {"trail", "name", "status"}:
                        data["trails"].append(
                            {
                                "name": name,
                                "status": _status_from_element(cells[1]),
                            }
                        )

        lift_heading = soup.find(
            string=re.compile(r"^\s*Lift\s+Status\b", re.IGNORECASE)
        )
        if lift_heading:
            section = _find_section(soup, r"^\s*Lift\s+Status\b")
            if section:
                data["lifts"].extend(_parse_status_list(section.select_one("ul")))
                for table in section.find_all("table"):
                    for row in table.find_all("tr"):
                        cells = row.find_all(["td", "th"])
                        if len(cells) < 2:
                            continue
                        name = cells[0].get_text(" ", strip=True)
                        if name and name.lower() not in {"lift", "name", "status"}:
                            data["lifts"].append(
                                {
                                    "name": name,
                                    "status": _status_from_element(cells[1]),
                                }
                            )

        data["trails"] = _unique_status_items(data["trails"])
        data["lifts"] = _unique_status_items(data["lifts"])
        data["trails_summary"] = {
            "open": sum(item["status"] == "open" for item in data["trails"]),
            "total": len(data["trails"]),
        }
        data["lifts_summary"] = {
            "open": sum(item["status"] == "open" for item in data["lifts"]),
            "total": len(data["lifts"]),
        }
        return data
    finally:
        driver.quit()


def _find_section(soup, pattern):
    heading = soup.find(
        ["h1", "h2", "h3", "h4", "h5", "h6"],
        string=re.compile(pattern, re.IGNORECASE),
    )
    return heading.find_parent(["div", "section"]) if heading else None


def _parse_snow_conditions(section):
    conditions = {}
    condition_list = section.select_one("#hill_conditions_info2")
    if condition_list:
        for item in condition_list.find_all("li", recursive=False):
            label = " ".join(
                text.strip()
                for text in item.find_all(string=True, recursive=False)
                if text.strip()
            )
            value_element = item.find("span", recursive=False)
            value = value_element.get_text(" ", strip=True) if value_element else ""
            normalized_label = label.lower()
            if normalized_label.startswith("base") and not _is_placeholder(value):
                conditions["base_depth"] = value
            elif normalized_label.startswith("new snow") and not _is_placeholder(value):
                conditions["new_snow"] = value
            elif normalized_label.startswith("snow making") and value:
                conditions["snowmaking"] = value

    surface = section.select_one(".surface_condition")
    if surface:
        surface_text = surface.get_text(" ", strip=True)
        if surface_text:
            conditions["surface"] = surface_text
    return conditions


def _parse_trail_lines(section):
    trails = []
    for column in section.select(".row > div"):
        name_parts = []
        for child in column.children:
            if isinstance(child, NavigableString):
                name_parts.append(str(child))
            elif child.name == "span":
                name = " ".join(" ".join(name_parts).split())
                if name:
                    trails.append(
                        {"name": name, "status": _status_from_element(child)}
                    )
                name_parts = []
            elif child.name == "br":
                name_parts = []
    return trails


def _parse_status_list(status_list):
    if not status_list:
        return []
    items = []
    for item in status_list.find_all("li", recursive=False):
        name = " ".join(
            text.strip()
            for text in item.find_all(string=True, recursive=False)
            if text.strip()
        )
        if name:
            items.append(
                {"name": name, "status": _status_from_element(item)}
            )
    return items


def _status_from_element(element):
    text = element.get_text(" ", strip=True)
    image = element.find("img")
    image_source = image.get("src", "").lower() if image else ""
    if any(marker in image_source for marker in ["tick", "check", "open", "yes"]):
        return "open"
    if any(marker in image_source for marker in ["cross", "close", "no"]):
        return "closed"
    return "open" if _is_open(text) else "closed"


def _is_placeholder(value):
    return value.strip().lower() in {"", "cm", "in", "inches", "n/a", "na", "-"}


def _is_open(value):
    return any(marker in value.lower() for marker in ["open", "✓", "yes", "●"])


def _unique_status_items(items):
    seen = set()
    unique = []
    for item in items:
        name = item.get("name", "")
        if name and name not in seen:
            seen.add(name)
            unique.append(item)
    return unique


def main():
    payload = {
        **to_weather_dto(get_trail_status()),
        "resortId": RESORT_ID,
        "sourceUrl": URL,
        "updatedAt": int(time.time() * 1000),
    }
    output_file = os.path.join(os.path.dirname(__file__), "weather-and-status.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
