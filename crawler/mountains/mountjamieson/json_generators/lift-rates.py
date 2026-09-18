import json
import os
import time

SOURCE_URL = "https://www.mountjamieson.ca/"
PAGE_URL = "https://www.mountjamieson.ca/day-passes"
RESORT_ID = "mount-jamieson"


def get_lift_rates():
    return {"day-week": {"adults": "$62.50", "youth": "$51.50", "seniors": "$51.50"}, "day-weekend": {"adults": "$62.50", "youth": "$51.50", "seniors": "$51.50"}}


def main():
    payload = {"rates": get_lift_rates(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "lift-rates.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
