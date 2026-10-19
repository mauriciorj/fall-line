import json
import os
import time

RESORT_ID = "big-white"
SOURCE_URL = "https://www.bigwhite.com/"
DAYS = ("sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday")


def get_hours():
    return {day: "closed" for day in DAYS}


def main():
    payload = {"hours": get_hours(), "resortId": RESORT_ID, "sourceUrl": SOURCE_URL, "updatedAt": int(time.time() * 1000)}
    with open(os.path.join(os.path.dirname(__file__), "hours-of-operation.json"), "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
