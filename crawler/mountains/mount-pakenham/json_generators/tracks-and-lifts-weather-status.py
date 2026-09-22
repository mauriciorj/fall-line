import json
import os
import time

SOURCE_URL = "https://shop.mountpakenham.com/"
RESORT_ID = "mount-pakenham"
LIFTS = ("Main Lift", "Cameron Lift", "Pakenham Lift", "Carpet Lift", "Handle Tow", "Learning Carpet")
TRACKS = {
    "The Loop": "green",
    "Lower Slowpoke": "green",
    "Middle Slowpoke": "green",
    "Upper Slowpoke": "blue",
    "Frank's Run": "green",
    "Crossover": "green",
    "Wizard": "green",
    "Lower Exhibition": "blue",
    "Clifford": "blue",
    "Snow Rider": "blue",
    "Slalom": "black",
    "Upper Exhibition": "black",
    "Porcupine": "black",
    "Lower Porcupine": "black",
    "Angel's Kiss Glades": "black",
    "Devil's Challenge Glades": "black",
    "Gauntlet Glades": "black",
    "Fox Trot Glades": "black",
    "Bear Paw Glades": "black",
    "Crossover Glades": "black",
    "Deer Run Glades": "black",
    "Bark'n'Bite Glades": "black",
    "Forbidden Forest Glades": "black",
}


def get_status():
    return {
        "lifts": [{"name": name, "status": "closed"} for name in LIFTS],
        "tracks": [
            {"name": name, "status": "closed", "difficulty": difficulty}
            for name, difficulty in TRACKS.items()
        ],
        "terrainParks": [{"name": "Terrain Park", "status": "closed", "difficulty": "freeStyle"}],
    }


def main():
    payload = {**get_status(), "resortId": RESORT_ID, "sourceUrl": SOURCE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "tracks-and-lifts-weather-status.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
