import json
import os
import time

RESORT_ID = "adanac-ski-hill"
SOURCE_URL = "https://www.greatersudbury.ca/play/ski-hills/adanac-ski-hill/"
TRACKS = (
    ("Easy Rider", "green"),
    ("Ellis Hazen", "blue"),
    ("Glades", "black"),
    ("Friendly Giant", "blue"),
    ("Inco", "blue"),
    ("Beginner Area", "green"),
    ("Double Trouble", "black"),
)


def get_status():
    return {
        "lifts": [{"name": "New Quad", "status": "not informed"}],
        "tracks": [
            {"name": name, "difficulty": difficulty, "status": "not informed"}
            for name, difficulty in TRACKS
        ],
        "terrainParks": [],
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
