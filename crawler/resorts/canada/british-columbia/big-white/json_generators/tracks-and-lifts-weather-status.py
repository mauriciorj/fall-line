import json
import os
import time

RESORT_ID = "big-white"
SOURCE_URL = "https://www.bigwhite.com/"


def get_status():
    return {"lifts": [], "tracks": [], "terrainParks": []}


def main():
    payload = {**get_status(), "resortId": RESORT_ID, "sourceUrl": SOURCE_URL, "updatedAt": int(time.time() * 1000)}
    with open(os.path.join(os.path.dirname(__file__), "tracks-and-lifts-weather-status.json"), "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
