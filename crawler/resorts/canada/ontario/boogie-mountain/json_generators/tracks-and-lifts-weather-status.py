import json
import os
import time

SOURCE_URL = "https://boogiemountain.com/the-mountain/"
RESORT_ID = "boogie-mountain"
TRACKS = {
    "Gord's Run": "blue",
    "Boogie Run": "black",
    "Speedo": "black",
    "Nose Dive": "blue",
    "Round About": "green",
    "Stellar Cellar": "black",
    "7 Leonard's Leap": "doubleBlack",
    "Main": "blue",
    "Fairhall": "blue",
    "Boomerang": "blue",
    "Bonzai": "green",
}
TERRAIN_PARKS = ("Skdol Yard",)


def get_status():
    return {
        "lifts": [],
        "tracks": [
            {"name": name, "status": "closed", "difficulty": difficulty}
            for name, difficulty in TRACKS.items()
        ],
        "terrainParks": [
            {"name": name, "status": "closed", "difficulty": "freeStyle"}
            for name in TERRAIN_PARKS
        ],
    }


def main():
    payload = {
        **get_status(),
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
