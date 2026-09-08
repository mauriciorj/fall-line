import json
import os
import re
import sys
import time

from bs4 import BeautifulSoup
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

        snow_heading = soup.find(string=re.compile(r"Snow\s*Conditions", re.IGNORECASE))
        if snow_heading:
            parent = snow_heading.find_parent()
            section = parent.find_parent(["div", "section"]) if parent else None
            if section:
                for item in section.find_all(["p", "span", "div", "li"]):
                    text = item.get_text(" ", strip=True)
                    if not text or len(text) >= 200:
                        continue
                    if re.search(r"base|depth", text, re.IGNORECASE):
                        data["snow_conditions"]["base_depth"] = text
                    elif re.search(r"new\s*snow|fresh", text, re.IGNORECASE):
                        data["snow_conditions"]["new_snow"] = text
                    elif re.search(r"surface|condition", text, re.IGNORECASE):
                        data["snow_conditions"]["surface"] = text
                    elif re.search(r"temp|temperature|°", text, re.IGNORECASE):
                        data["snow_conditions"]["temperature"] = text
                    elif re.search(r"last\s*updated|updated", text, re.IGNORECASE):
                        data["snow_conditions"]["last_updated"] = text

        trail_heading = soup.find(string=re.compile(r"Trail\s*Status", re.IGNORECASE))
        if trail_heading:
            parent = trail_heading.find_parent()
            section = parent.find_parent(["div", "section"]) if parent else None
            if section:
                for table in section.find_all("table"):
                    for row in table.find_all("tr"):
                        cells = row.find_all(["td", "th"])
                        if len(cells) < 2:
                            continue
                        name = cells[0].get_text(" ", strip=True)
                        status_text = cells[1].get_text(" ", strip=True)
                        if name and name.lower() not in {"trail", "name", "status"}:
                            data["trails"].append(
                                {
                                    "name": name,
                                    "status": "open" if _is_open(status_text) else "closed",
                                }
                            )
                if not data["trails"]:
                    for item in section.find_all("li"):
                        text = item.get_text(" ", strip=True)
                        if text:
                            data["trails"].append(
                                {"name": text, "status": "open" if _is_open(text) else "closed"}
                            )

        if not data["trails"]:
            for element in soup.find_all(
                class_=lambda value: value
                and any(key in str(value).lower() for key in ["trail", "run", "slope", "status"])
            ):
                text = element.get_text(" ", strip=True)
                if text and len(text) < 100:
                    data["trails"].append(
                        {"name": text, "status": "open" if _is_open(text) else "closed"}
                    )

        lift_heading = soup.find(string=re.compile(r"Lift\s*Status|Lifts", re.IGNORECASE))
        if lift_heading:
            parent = lift_heading.find_parent()
            section = parent.find_parent(["div", "section"]) if parent else None
            if section:
                for item in section.find_all(["li", "tr", "div"]):
                    text = item.get_text(" ", strip=True)
                    if text and len(text) < 100:
                        data["lifts"].append(
                            {"name": text, "status": "open" if _is_open(text) else "closed"}
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
