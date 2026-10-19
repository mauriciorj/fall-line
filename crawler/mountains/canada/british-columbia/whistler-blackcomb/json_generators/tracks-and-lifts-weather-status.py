import json
import os
import time

RESORT_ID = "whistler-blackcomb"
SOURCE_URL = "https://www.whistlerblackcomb.com/the-mountain/mountain-conditions/terrain-and-lift-status.aspx"


def get_status():
    return {"lifts": [], "tracks": [], "terrainParks": []}


def main():
    payload = {
        **get_status(),
        "resortId": RESORT_ID,
        "sourceUrl": SOURCE_URL,
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
