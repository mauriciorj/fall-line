import json
import os
import time

SOURCE_URL = "https://antoinemountain.ca/"
PAGE_URL = "https://antoinemountain.ca/pages/trail-conditions"
RESORT_ID = "antoine-mountain"

TRACKS = ("Voyageur", "Look Out", "Static", "Nice 'n' Easy", "Portage", "Handle Tow", "Mattawa", "Ottawa", "Dambuster", "Laurentian", "Bowl", "Kate Pace", "Chute", "Cliffhanger", "Spillway")
LIFTS = ("Skydigger", "Antoine Mountain Handle Tow")
DIFFICULTIES = {"Voyageur": "green", "Look Out": "green", "Static": "green", "Nice 'n' Easy": "green", "Portage": "blue", "Handle Tow": "green", "Mattawa": "blue", "Ottawa": "blue", "Dambuster": "black", "Laurentian": "black", "Bowl": "black", "Kate Pace": "blue", "Chute": "black", "Cliffhanger": "black", "Spillway": "green"}


def get_status():
    return {
        "lifts": [{"name": name, "status": "closed"} for name in LIFTS],
        "tracks": [{"name": name, "status": "closed", "difficulty": DIFFICULTIES[name]} for name in TRACKS],
        "terrainParks": [],
    }


def main():
    payload = {**get_status(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "tracks-and-lifts-weather-status.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
