import json
import os
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL = "https://www.discoverchicopee.com/activity-report"
RESORT_ID = "chicopee"
LIFT_NAMES = (
    "Surface Lift #1",
    "Surface Lift #2",
    "Surface Lift #3",
    "Red Chairlift",
    "North Chairlift",
    "Applebowl Chairlift",
)
TRACK_NAMES = (
    "Discover",
    "Adventure",
    "Bridge",
    "Freedom",
    "Mount St. Louis Moonstone Way",
    "Wishbone",
    "Easy Rider",
    "North",
    "Mic Mac",
    "Chicane",
    "Roughshod",
    "Applebowl",
    "Racer's Alley",
    "The Park",
)
TRACK_DIFFICULTIES = {
    "Discover": "green",
    "Adventure": "green",
    "Bridge": "blue",
    "Freedom": "blue",
    "Mount St. Louis Moonstone Way": "green",
    "Wishbone": "blue",
    "Easy Rider": "black",
    "North": "blue",
    "Mic Mac": "black",
    "Chicane": "black",
    "Roughshod": "black",
    "Applebowl": "black",
    "Racer's Alley": "blue",
    "The Park": "freeStyle",
}


def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)


def is_open(value):
    return any(marker in value.lower() for marker in ("open", "✓", "yes"))


def normalize_inventory(lifts, tracks):
    lift_statuses = {item["name"]: item["status"] for item in lifts}
    track_statuses = {item["name"]: item["status"] for item in tracks}
    return {
        "lifts": [
            {"name": name, "status": lift_statuses.get(name, "closed")}
            for name in LIFT_NAMES
        ],
        "tracks": [
            {
                **(
                    {"difficulty": TRACK_DIFFICULTIES[name]}
                    if name in TRACK_DIFFICULTIES
                    else {}
                ),
                "name": name,
                "status": track_statuses.get(name, "closed"),
            }
            for name in TRACK_NAMES
        ],
    }


def get_status():
    driver = get_driver()
    try:
        driver.get(URL)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")
        lifts = []
        tracks = []
        for section in soup.find_all(
            class_=lambda value: value
            and ("lift" in str(value).lower() or "chair" in str(value).lower())
        ):
            text = section.get_text(separator="|", strip=True)
            if text:
                name = text.split("|")[0]
                lifts.append({"name": name, "status": "open" if is_open(text) else "closed"})

        for section in soup.find_all(
            class_=lambda value: value
            and any(key in str(value).lower() for key in ("trail", "run", "slope"))
        ):
            text = section.get_text(separator="|", strip=True)
            if text:
                name = text.split("|")[0]
                tracks.append(
                    {
                        "difficulty": TRACK_DIFFICULTIES.get(name, "green"),
                        "name": name,
                        "status": "open" if is_open(text) else "closed",
                    }
                )
        return normalize_inventory(lifts, tracks)
    finally:
        driver.quit()


def main():
    payload = {
        **get_status(),
        "resortId": RESORT_ID,
        "sourceUrl": URL,
        "updatedAt": int(time.time() * 1000),
    }
    output_file = os.path.join(
        os.path.dirname(__file__), "tracks-and-lifts-weather-status.json"
    )
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
