import json
import os
import time

RESORT_ID = "lively-ski-hill"
SOURCE_URL = "https://www.greatersudbury.ca/play/ski-hills/lively-ski-hill/"


def main():
    payload = {
        "lifts": [{"name": "Lively Platter", "status": "closed"}],
        "tracks": [
            {"name": "Old Tow", "difficulty": "blue", "status": "not informed"},
            {"name": "Superman", "difficulty": "blue", "status": "not informed"},
            {"name": "Nightmare", "difficulty": "black", "status": "not informed"},
            {"name": "Beginner Run", "difficulty": "green", "status": "not informed"},
        ],
        "terrainParks": [],
        "resortId": RESORT_ID,
        "sourceUrl": SOURCE_URL,
        "updatedAt": int(time.time() * 1000),
    }
    output_file = os.path.join(os.path.dirname(__file__), "tracks-and-lifts-weather-status.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
