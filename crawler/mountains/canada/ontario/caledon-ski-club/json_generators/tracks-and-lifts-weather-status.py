import json
import os
import time

from bs4 import BeautifulSoup, NavigableString
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL = "https://caledonskiclub.com/private-lessons"
RESORT_ID = "caledon-ski-club"
TRACK_DIFFICULTIES = {
    "Alley Way": "blue",
    "Boughner's Boogie": "blue",
    "Carson's Run / Simon's Snow Park": "freestyle",
    "Dodds' Dip": "blue",
    "Eaton's Annex": "green",
    "Harold's Headstander": "black",
    "Holden's Hwy": "freestyle",
    "Kendall's Kandihar": "green",
    "Kenne's Kicker": "black",
    "Kids' Buel": "green",
    "Knight Flight": "black",
    "Larry's Line": "blue",
    "Lower Road": "green",
    "MacKenzie Trail": "blue",
    "Moonbeam": "freestyle",
    "O.K. Ross Run": "blue",
    "Philpott's Folly": "blue",
    "Porter's Pipeline": "double-black",
    "Quick Link": "blue",
    "Roadrunner": "freestyle",
    "Sidewinder": "green",
    "Snowy's Glade": "black",
    "Soules' Skyway": "blue",
    "West Hill": "green",
    "Wortley's Wiggle": "black",
}


def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)


def status_from_element(element):
    text = element.get_text(" ", strip=True).lower()
    return "open" if any(marker in text for marker in ("open", "yes", "✓")) else "closed"


def parse_trail_lines(section):
    tracks = []
    for column in section.select(".row > div"):
        name_parts = []
        for child in column.children:
            if isinstance(child, NavigableString):
                name_parts.append(str(child))
            elif child.name == "span":
                name = " ".join(" ".join(name_parts).split())
                if name:
                    tracks.append(
                        {"name": name, "status": status_from_element(child)}
                    )
                name_parts = []
            elif child.name == "br":
                name_parts = []
    return tracks


def parse_status_list(status_list):
    if not status_list:
        return []
    tracks = []
    for item in status_list.find_all("li", recursive=False):
        name = " ".join(
            text.strip()
            for text in item.find_all(string=True, recursive=False)
            if text.strip()
        )
        if name:
            tracks.append({"name": name, "status": status_from_element(item)})
    return tracks


def get_tracks():
    driver = get_driver()
    try:
        driver.get(URL)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")
        section = soup.select_one("#tab_popup_hill")
        if not section:
            return []
        tracks = parse_trail_lines(section)
        tracks.extend(parse_status_list(section.select_one("ul.hill_status")))
        return tracks
    finally:
        driver.quit()


def normalize_tracks(scraped_tracks):
    statuses = {
        track["name"]: track.get("status", "closed")
        for track in scraped_tracks
        if track.get("name")
    }
    return [
        {
            "difficulty": difficulty,
            "name": name,
            "status": statuses.get(name, "closed"),
        }
        for name, difficulty in TRACK_DIFFICULTIES.items()
    ]


def main():
    payload = {
        "tracks": normalize_tracks(get_tracks()),
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
