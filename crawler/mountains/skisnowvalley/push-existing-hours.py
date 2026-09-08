import json
import os
import sys
import time

# Allow importing the shared Convex client from the parent directory.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from convex_client import push_resort_hours

RESORT_ID = "snow-valley-ski-resort"
SOURCE_URL = "https://www.skisnowvalley.com/about/"


def to_hours(hours_data):
    """
    Convert the nested hours dictionary into the normalized Convex hours shape.
    """
    normalized_hours = []
    for section_name, section_value in hours_data.items():
        if not section_value:
            continue

        first_val = next(iter(section_value.values()))

        if isinstance(first_val, dict):
            activities = []
            for activity_name, days in section_value.items():
                hours = [
                    {"day": day_name, "time": time}
                    for day_name, time in days.items()
                ]
                activities.append({"name": activity_name, "hours": hours})
            normalized_hours.append({"name": section_name, "activities": activities})
        else:
            hours = [
                {"day": day_name, "time": time}
                for day_name, time in section_value.items()
            ]
            normalized_hours.append({"name": section_name, "hours": hours})

    return normalized_hours


def main():
    json_path = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    if not os.path.isfile(json_path):
        print(f"No hours file found at {json_path}. Run hours-of-operation.py first.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        hours_data = json.load(f)

    hours = to_hours(hours_data)
    updated_at_ms = int(time.time() * 1000)

    result = push_resort_hours(
        RESORT_ID,
        SOURCE_URL,
        hours,
        updated_at_ms=updated_at_ms,
    )

    if result is not None:
        print("Pushed to Convex:", result)
    else:
        print("Convex not configured; nothing was pushed.")


if __name__ == "__main__":
    main()
