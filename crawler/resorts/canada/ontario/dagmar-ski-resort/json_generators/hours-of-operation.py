import json
import os
import time

RESORT_ID = "dagmar-ski-resort"
SOURCE_URL = "https://www.skidagmar.com/alpine-rates/"
HOURS = {
    "sunday": "closed",
    "monday": "10am - 4pm",
    "tuesday": "10am - 4pm",
    "wednesday": "10am - 4pm",
    "thursday": "9am - 4pm",
    "friday": "10am - 4pm",
    "saturday": "closed",
}


def get_hours():
    return HOURS.copy()


def main():
    payload = {
        "hours": get_hours(),
        "resortId": RESORT_ID,
        "sourceUrl": SOURCE_URL,
        "updatedAt": int(time.time() * 1000),
    }
    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
