import json
import os
import time

SOURCE_URL = "https://www.lochlomond.ca/"
PAGE_URL = "https://www.lochlomond.ca/conditions/"
RESORT_ID = "loch-lomond"
LIFTS = ("South Chairlift", "Snoopy Chairlift", "North Chairlift")
TRACKS = ("Upper Sunbowl", "Lower Sunbowl", "Cliff", "Mullet", "Upper Pine", "Lower Pine", "Pine Glades", "Lower Sunbowl", "Chicken", "Kitzbuel", "Upper Maple", "Lower Maple", "Zipper", "Birch", "Old Joe's", "Giant", "Jolly Giant", "Devil's Dive", "Devil's Playground")
DIFFICULTIES = {"Upper Sunbowl": "green", "Lower Sunbowl": "green", "Cliff": "blue", "Mullet": "blue", "Upper Pine": "blue", "Lower Pine": "blue", "Pine Glades": "blue", "Chicken": "green", "Kitzbuel": "green", "Upper Maple": "blue", "Lower Maple": "blue", "Zipper": "blue", "Birch": "black", "Old Joe's": "black", "Giant": "black", "Jolly Giant": "doubleBlack", "Devil's Dive": "doubleBlack", "Devil's Playground": "doubleBlack"}


def get_status():
    return {"lifts": [{"name": name, "status": "closed"} for name in LIFTS], "tracks": [{"name": name, "status": "closed", "difficulty": DIFFICULTIES[name]} for name in TRACKS], "terrainParks": [{"name": "Terrain Park", "status": "closed", "difficulty": "freeStyle"}]}


def main():
    payload = {**get_status(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "tracks-and-lifts-weather-status.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
