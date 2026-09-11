import json
import os
import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from dtos import to_weather_dto

URL = "https://www.bluemountain.ca/mountain/mountain-report"
RESORT_ID = "blue-mountain"


def get_trail_status():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(URL)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        data = {"conditions": {}, "lifts": [], "trails": {}}

        weather_elements = soup.find_all(
            class_=lambda value: value and "WeatherWidget" in str(value)
        )
        for element in weather_elements:
            match = re.search(r"(-?\d+)\s*°", element.get_text("|", strip=True))
            if match:
                data["conditions"]["temperature"] = f"{match.group(1)}°C"

        updated = soup.find(string=lambda value: value and "Updated" in value)
        if updated:
            data["conditions"]["last_updated"] = updated.strip()

        for lift in soup.find_all(class_=lambda value: value and "Lift_lift__" in str(value)):
            parts = lift.get_text("|", strip=True).split("|")
            if len(parts) >= 3:
                data["lifts"].append(
                    {"name": parts[0], "hours": parts[1], "status": parts[2]}
                )

        for accordion in soup.find_all(
            class_=lambda value: value and "Accordion_accordion__" in str(value)
        ):
            title = accordion.find(class_=lambda value: value and "accordionTitle" in str(value))
            area = title.get_text(strip=True).lower() if title else "all"
            trail_list = accordion.find(class_=lambda value: value and "trailList" in str(value))
            if not trail_list:
                continue
            data["trails"].setdefault(area, [])
            for trail in trail_list.find_all(recursive=False):
                parts = trail.get_text("|", strip=True).split("|")
                if len(parts) >= 2:
                    data["trails"][area].append({"name": parts[0], "status": parts[1]})

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
