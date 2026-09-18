import json
import os
import time

SOURCE_URL = "https://www.mountjamieson.ca/"
PAGE_URL = "https://www.mountjamieson.ca/trail-map-conditions"
RESORT_ID = "mount-jamieson"
LIFTS = ("Skyway", "Downhill")
TRACKS = ()


def get_status():
    return {"lifts": [{"name": name, "status": "closed"} for name in LIFTS], "tracks": [], "terrainParks": []}


def main():
    payload = {**get_status(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "tracks-and-lifts-weather-status.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
