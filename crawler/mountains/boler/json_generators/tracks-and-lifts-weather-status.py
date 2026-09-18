import json
import os
import time

SOURCE_URL = "https://www.bolermountain.com/"
PAGE_URL = "https://www.bolermountain.com/"
RESORT_ID = "boler-mountain"


def get_status():
    return {"lifts": [{"name": f"Lift {index}", "status": "closed"} for index in range(1, 5)], "tracks": [], "terrainParks": []}


def main():
    payload = {**get_status(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "tracks-and-lifts-weather-status.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
