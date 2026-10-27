import json
import os
import time

RESORT_ID = "atikokan"
SOURCE_URL = "https://visitatikokan.com/experiences/mount-fairweather/"


def get_rentals():
    return {}


def main():
    payload = {
        "rentals": get_rentals(),
        "resortId": RESORT_ID,
        "sourceUrl": SOURCE_URL,
        "updatedAt": int(time.time() * 1000),
    }
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
