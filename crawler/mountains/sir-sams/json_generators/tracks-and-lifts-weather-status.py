import json
import os
import time

SOURCE_URL = "https://www.sirsams.ca/"
PAGE_URL = "https://www.sirsams.ca/resort-information"
RESORT_ID = "sir-sams"
LIFTS = ("Main Street", "North Quad", "South Chair", "Handle Tow", "Eagle View Quad")
TRACKS = {
    "Lover's Lane": "blue",
    "Heartbreaker": "black",
    "Banana": "blue",
    "Cash Register": "blue",
    "Kingston": "blue",
    "Parkway": "black",
    "Ali's Alley": "green",
    "Fred's Way": "green",
    "Crash n' Carry": "black",
    "Birdwatcher": "black",
    "Dingle": "green",
    "Dangle": "green",
    "Ridge": "green",
    "Run": "green",
}


def get_status():
    return {
        "lifts": [{"name": name, "status": "closed"} for name in LIFTS],
        "tracks": [
            {"name": name, "status": "closed", "difficulty": difficulty}
            for name, difficulty in TRACKS.items()
        ],
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
