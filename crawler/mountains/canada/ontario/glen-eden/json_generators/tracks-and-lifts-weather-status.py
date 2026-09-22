import json
import os
import time

RESORT_ID = "glen-eden"
SOURCE_URL = "https://gleneden.on.ca/at-glen-eden/slope-conditions/"
RUNS = (
    (None, "Escarpment Run"),
    (None, "Night Hawk"),
    (None, "Butternut"),
    (None, "Falcon"),
    (None, "Scimitar"),
    (None, "Sidewinder"),
    (None, "Twister"),
    (None, "Boomerang"),
    (None, "Challenger"),
    (None, "Quarry Run"),
    ("The Galaxy", "Comet"),
    ("The Galaxy", "Little Dipper"),
    ("The Galaxy", "Milky Way"),
    ("The Galaxy", "Shooting Star"),
    ("West Beginner Area", "Bumble Bee"),
    ("West Beginner Area", "Grasshopper"),
    ("West Beginner Area", "Monarch"),
)
TRACK_DIFFICULTIES = {
    "Escarpment Run": "green",
    "Night Hawk": "green",
    "Butternut": "blue",
    "Falcon": "blue",
    "Scimitar": "blue",
    "Sidewinder": "blue",
    "Twister": "blue",
    "Boomerang": "black",
    "Challenger": "black",
    "Quarry Run": "freestyle",
    "Comet": "green",
    "Little Dipper": "green",
    "Milky Way": "green",
    "Shooting Star": "green",
    "Bumble Bee": "green",
    "Grasshopper": "green",
    "Monarch": "green",
}
LIFTS = (
    (None, "Limestone Chairlift"),
    (None, "Ridge Chairlift"),
    (None, "Updraft Chairlift"),
    ("The Galaxy", "Shuttle Carpet"),
    ("West Beginner Area", "Caterpillar Carpet"),
    ("West Beginner Area", "Cricket Carpet"),
)


def get_status():
    return {
        "lifts": [
            {
                **({"area": area} if area else {}),
                "name": name,
                "status": "closed",
            }
            for area, name in LIFTS
        ],
        "tracks": [
            {
                **({"area": area} if area else {}),
                "difficulty": TRACK_DIFFICULTIES[name],
                "name": name,
                "status": "closed",
            }
            for area, name in RUNS
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
