import json
import os
import time

SOURCE_URL = "https://calabogie.com/"
PAGE_URL = "https://calabogie.com/trail-status/"
RESORT_ID = "calabogie-peaks"
LIFTS = ("Edelweiss", "Lakeside", "Magic Carpet")
TRACKS = ("Beginner", "Bambi", "Big Easy", "Cannonball", "Chute", "Devil's Elbow", "Eagle's Nest", "Express", "Highlander", "Lower Main", "Main Street", "Maple", "Mountain View", "Race Hill", "Ridge Run", "Rocky Ridge", "Sidewinder", "Snowbird", "The Bowl", "The Glades")
DIFFICULTIES = {"Beginner": "green", "Bambi": "green", "Big Easy": "green", "Cannonball": "blue", "Chute": "black", "Devil's Elbow": "blue", "Eagle's Nest": "black", "Express": "blue", "Highlander": "black", "Lower Main": "green", "Main Street": "blue", "Maple": "green", "Mountain View": "green", "Race Hill": "black", "Ridge Run": "blue", "Rocky Ridge": "blue", "Sidewinder": "blue", "Snowbird": "green", "The Bowl": "black", "The Glades": "doubleBlack"}


def get_status():
    return {"lifts": [{"name": name, "status": "closed"} for name in LIFTS], "tracks": [{"name": name, "status": "closed", "difficulty": DIFFICULTIES[name]} for name in TRACKS], "terrainParks": []}


def main():
    payload = {**get_status(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "tracks-and-lifts-weather-status.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
