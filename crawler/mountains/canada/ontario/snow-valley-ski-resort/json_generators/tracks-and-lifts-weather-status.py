import json
import os
import time

RESORT_ID = "snow-valley-ski-resort"
SOURCE_URL = "https://www.skisnowvalley.com/plan/weather-webcams/"
TRACKS = (
    ("green", "garfield"),
    ("green", "snoopy"),
    ("blue", "trudys way"),
    ("black", "pennys"),
    ("black", "schuss"),
    ("green", "highland trail"),
    ("green", "family"),
    ("black", "racer"),
    ("black", "hard knox"),
    ("blue", "front"),
    ("blue", "whistler"),
    ("green", "recken run"),
    ("blue", "keith rolls"),
    ("doubleBlack", "vertigo"),
    ("black", "huxtable"),
    ("black", "oh chute"),
    ("freeStyle", "easy does it"),
    ("green", "alc 1"),
    ("green", "alc 2"),
    ("green", "alc 3"),
    ("green", "kidz village"),
)
LIFTS = (
    "quad chair",
    "wide load chair",
    "triple chair",
    "snowflake express",
    "wonderland express",
    "polar express",
    "magic carpet",
    "kidz village express",
)


def get_status():
    return {
        "lifts": [{"name": name, "status": "closed"} for name in LIFTS],
        "tracks": [
            {"difficulty": difficulty, "name": name, "status": "closed"}
            for difficulty, name in TRACKS
        ],
    }


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
