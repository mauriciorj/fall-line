import json
import os
import time

SOURCE_URL = "https://www.sirsams.ca/"
PAGE_URL = "https://www.sirsams.ca/winter/rentals"
RESORT_ID = "sir-sams"


def get_rentals():
    return {"ski": {"adults": "$64", "youth": "$50"}, "snowboard": {"adults": "$64", "youth": "$50"}, "items": {"skis": "$32", "snowboard": "$32", "boots": "$34", "helmet": "$15", "poles": "$15"}}


def main():
    payload = {"rentals": get_rentals(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
