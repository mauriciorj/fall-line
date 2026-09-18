import json
import os
import time

SOURCE_URL = "https://shop.mountpakenham.com/"
RESORT_ID = "mount-pakenham"
LIFTS = ("Main Lift", "Cameron Lift", "Pakenham Lift", "Carpet Lift", "Handle Tow", "Learning Carpet")
TRACKS = ("Beginner Centre", "The Loop", "Wizard", "Slowpoke", "Exhibition", "Clifford", "Snowrider", "Slalom", "Porcupine", "Glades", "Terrain Park", "Snowshoe Trails")
DIFFICULTIES = {"Beginner Centre": "green", "The Loop": "green", "Wizard": "green", "Slowpoke": "green", "Exhibition": "blue", "Clifford": "blue", "Snowrider": "blue", "Slalom": "black", "Porcupine": "green", "Glades": "black", "Terrain Park": "freeStyle", "Snowshoe Trails": "green"}


def get_status():
    tracks = [{"name": name, "status": "closed", "difficulty": DIFFICULTIES[name]} for name in TRACKS if name != "Terrain Park"]
    terrain_parks = [{"name": "Terrain Park", "status": "closed", "difficulty": "freeStyle"}]
    return {"lifts": [{"name": name, "status": "closed"} for name in LIFTS], "tracks": tracks, "terrainParks": terrain_parks}


def main():
    payload = {**get_status(), "resortId": RESORT_ID, "sourceUrl": SOURCE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "tracks-and-lifts-weather-status.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
