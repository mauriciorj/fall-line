import json
import os
import time

SOURCE_URL = "https://skihiddenvalley.ca/"
PAGE_URL = "https://shop.skihiddenvalley.ca/rentals"
RESORT_ID = "hidden-valley-highlands"


def get_rentals():
    return {"ski": {"adults": "$40", "youth": "$40"}, "snowboard": {"adults": "$40", "youth": "$40"}, "items": {}}


def main():
    payload = {"rentals": get_rentals(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
