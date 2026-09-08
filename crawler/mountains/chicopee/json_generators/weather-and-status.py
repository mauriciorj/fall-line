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

URL = "https://www.discoverchicopee.com/activity-report"
RESORT_ID = "chicopee"


def _is_open(value):
    return any(marker in value.lower() for marker in ["open", "✓", "yes"])


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
        data = {
            "lifts": [],
            "trails": [],
            "terrain_parks": [],
            "conditions": {},
        }

        for section in soup.find_all(
            class_=lambda value: value
            and ("lift" in str(value).lower() or "chair" in str(value).lower())
        ):
            text = section.get_text(separator="|", strip=True)
            if text:
                data["lifts"].append(
                    {
                        "name": text.split("|")[0],
                        "status": "open" if _is_open(text) else "closed",
                    }
                )

        for section in soup.find_all(
            class_=lambda value: value
            and any(key in str(value).lower() for key in ["trail", "run", "slope"])
        ):
            text = section.get_text(separator="|", strip=True)
            if text:
                data["trails"].append(
                    {
                        "name": text.split("|")[0],
                        "status": "open" if _is_open(text) else "closed",
                    }
                )

        for section in soup.find_all(
            class_=lambda value: value
            and any(key in str(value).lower() for key in ["park", "terrain"])
        ):
            text = section.get_text(separator="|", strip=True)
            if text:
                data["terrain_parks"].append(
                    {
                        "name": text.split("|")[0],
                        "status": "open" if _is_open(text) else "closed",
                    }
                )

        for table in soup.find_all("table"):
            for row in table.find_all("tr")[1:]:
                cells = row.find_all(["td", "th"])
                if len(cells) < 2:
                    continue
                name = cells[0].get_text(" ", strip=True)
                status_text = cells[1].get_text(" ", strip=True)
                data["trails"].append(
                    {"name": name, "status": "open" if _is_open(status_text) else "closed"}
                )

        for item in soup.find_all("li"):
            text = item.get_text(" ", strip=True)
            classes = " ".join(item.get("class", []))
            if text and any(key in classes.lower() for key in ["status", "trail", "lift", "run"]):
                data["trails"].append(
                    {"name": text.split()[0], "status": "open" if _is_open(text) else "closed"}
                )

        data["lifts"] = _unique(data["lifts"])
        data["trails"] = _unique(data["trails"])
        data["terrain_parks"] = _unique(data["terrain_parks"])
        data["lifts_summary"] = {
            "open": sum(item["status"] == "open" for item in data["lifts"]),
            "total": len(data["lifts"]),
        }
        data["trails_summary"] = {
            "open": sum(item["status"] == "open" for item in data["trails"]),
            "total": len(data["trails"]),
        }
        data["parks_summary"] = {
            "open": sum(item["status"] == "open" for item in data["terrain_parks"]),
            "total": len(data["terrain_parks"]),
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
