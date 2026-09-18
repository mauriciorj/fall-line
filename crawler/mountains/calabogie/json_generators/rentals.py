import json
import os
import time

SOURCE_URL = "https://calabogie.com/"
PAGE_URL = "https://calabogie.com/winter/rentals/"
RESORT_ID = "calabogie-peaks"


def get_rentals():
    return {"ski": {"adults": "$40", "youth": "$40"}, "snowboard": {"adults": "$40", "youth": "$40"}, "items": {"skis": "$30", "snowboard": "$30", "snowshoes": "$15"}}


def main():
    payload = {"rentals": get_rentals(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
