import json
import os
import time

RESORT_ID = "horseshoe-valley-resort"
SOURCE_URL = "https://horseshoeresort.com/ski-report-trails/"
RUNS = (
    ("green", "Ponyback"),
    ("green", "Pinto"),
    ("green", "Hungry Hollow"),
    ("green", "Roundup"),
    ("green", "Donkey Serenade"),
    ("green", "Pony Express"),
    ("green", "Canter"),
    ("green", "Mule Train"),
    ("blue", "Steeplechase"),
    ("blue", "Flying Mare"),
    ("blue", "Pony Tail"),
    ("blue", "Ramey's Return"),
    ("blue", "Saddleback"),
    ("blue", "Stallion Slide"),
    ("blue", "Duster"),
    ("blue", "Nightmare Ride"),
    ("blue", "Stampede"),
    ("blue", "The Wave"),
    ("blue", "Shaggy Mane"),
    ("blue", "The Zipper"),
    ("blue", "Bushwacker"),
    ("blue", "Bronco"),
    ("black", "Race Hill"),
    ("black", "Horsefeathers"),
    ("freeStyle", "Horsefly Hop"),
    ("freeStyle", "Bullpen"),
)
LIFTS = (
    "Kimbles Carpet",
    "Snow School Express",
    "Double Chair",
    "Copeland Express 6 Person Chair",
    "High Rider Quad",
    "Highland Express Quad",
)


def get_status():
    return {
        "lifts": [{"name": name, "status": "closed"} for name in LIFTS],
        "tracks": [
            {"difficulty": difficulty, "name": name, "status": "closed"}
            for difficulty, name in RUNS
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
