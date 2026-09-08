import json
import os
import sys
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dtos import to_weather_dto

URL = "https://gleneden.on.ca/at-glen-eden/slope-conditions/"
RESORT_ID = "glen-eden"


def _status_from_cell(cell):
    image = cell.find("img")
    if image:
        value = f"{image.get('alt', '')} {image.get('src', '')}".lower()
        if "open" in value or "green" in value:
            return "Open"
        if "closed" in value or "red" in value:
            return "Closed"
    return cell.get_text(" ", strip=True)


def _unique(items):
    seen = set()
    result = []
    for item in items:
        name = item.get("name", "")
        if name and name not in seen:
            seen.add(name)
            result.append(item)
    return result


def get_trail_status():
    print(f"Fetching {URL}...")
    options = Options()
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
        data = {"conditions": {}, "lifts": [], "trails": []}

        for text_node in soup.find_all(string=True):
            text = text_node.strip()
            lowered = text.lower()
            if "base depth" in lowered:
                data["conditions"]["base_depth"] = text
            elif "groomed" in lowered:
                data["conditions"]["snow_condition"] = text
            elif "new snow" in lowered:
                data["conditions"]["new_snow"] = text
            elif "snowmaking" in lowered:
                data["conditions"]["snowmaking"] = text

        for table in soup.find_all("table"):
            rows = table.find_all("tr")
            for row in rows[1:]:
                cells = row.find_all("td")
                if len(cells) < 2:
                    continue
                item = {
                    "name": cells[0].get_text(" ", strip=True),
                    "status": _status_from_cell(cells[1]),
                }
                if any(key in item["name"].lower() for key in ["lift", "carpet", "chair", "t-bar"]):
                    data["lifts"].append(item)
                else:
                    data["trails"].append(item)

        data["lifts"] = _unique(data["lifts"])
        data["trails"] = _unique(data["trails"])
        data["lifts_summary"] = {
            "open": sum("open" in item["status"].lower() for item in data["lifts"]),
            "total": len(data["lifts"]),
        }
        data["trails_summary"] = {
            "open": sum("open" in item["status"].lower() for item in data["trails"]),
            "total": len(data["trails"]),
        }
        return data
    finally:
        driver.quit()


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
