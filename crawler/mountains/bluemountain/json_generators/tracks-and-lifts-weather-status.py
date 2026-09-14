import json
import os
import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URL = "https://www.bluemountain.ca/mountain/mountain-report"
RESORT_ID = "blue-mountain"
DEFAULT_TRACK_AREA = "Multi-Use (Bike/Hike) Trails"
DEFAULT_TRACK_DIFFICULTY = "green"
DIFFICULTY_FIELDS = {
    "easy": "green",
    "medium": "blue",
    "hard": "black",
    "double black": "doubleBlack",
    "freestyle": "freeStyle",
    "free style": "freeStyle",
}


def normalize_difficulty(value):
    normalized = " ".join(value.lower().split())
    return DIFFICULTY_FIELDS.get(normalized)


def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    return webdriver.Chrome(options=options)


def get_status():
    driver = get_driver()
    try:
        driver.get(URL)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        raw_lifts = []
        raw_trails = []

        for lift in soup.find_all(class_=lambda value: value and "Lift_lift__" in str(value)):
            parts = lift.get_text("|", strip=True).split("|")
            if len(parts) >= 3:
                raw_lifts.append(
                    {"name": parts[0], "hours": parts[1], "status": parts[2]}
                )

        for accordion in soup.find_all(
            class_=lambda value: value and "Accordion_accordion__" in str(value)
        ):
            title = accordion.find(
                class_=lambda value: value and "accordionTitle" in str(value)
            )
            area = title.get_text(" ", strip=True) if title else "Unknown"
            trail_list = accordion.find(
                class_=lambda value: value and "trailList" in str(value)
            )
            if not trail_list:
                continue
            for trail in trail_list.find_all(recursive=False):
                parts = trail.get_text("|", strip=True).split("|")
                if len(parts) >= 2:
                    raw_trails.append(
                        {
                            "area": area,
                            "name": parts[0],
                            "status": parts[1],
                        }
                    )

        tracks = [
            {
                "area": DEFAULT_TRACK_AREA,
                "difficulty": normalize_difficulty(row.get("difficulty", ""))
                or DEFAULT_TRACK_DIFFICULTY,
                "name": row["name"],
                "status": row["status"],
            }
            for row in raw_lifts
        ]
        return {"lifts": raw_trails, "tracks": tracks}
    finally:
        driver.quit()


def main():
    payload = {
        **get_status(),
        "resortId": RESORT_ID,
        "sourceUrl": URL,
        "updatedAt": int(time.time() * 1000),
    }
    for track in payload["tracks"]:
        track.setdefault("area", DEFAULT_TRACK_AREA)
    output_file = os.path.join(
        os.path.dirname(__file__), "tracks-and-lifts-weather-status.json"
    )
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
