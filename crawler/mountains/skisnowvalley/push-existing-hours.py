import json
import os
import sys
import time

# Allow importing the shared Convex client from the parent directory.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from convex_client import push_resort_hours

RESORT_ID = "snow-valley-ski-resort"
RESORT_NAME = "Ski Snow Valley"
SOURCE_URL = "https://www.skisnowvalley.com/about/"


def to_convex_sections(hours_data):
    """
    Convert the nested hours dictionary into the normalized Convex sections shape.
    """
    sections = []
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
            sections.append({"name": section_name, "activities": activities})
        else:
            hours = [
                {"day": day_name, "time": time}
                for day_name, time in section_value.items()
            ]
            sections.append({"name": section_name, "hours": hours})

    return sections


def main():
    json_path = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    if not os.path.isfile(json_path):
        print(f"No hours file found at {json_path}. Run hours-of-operation.py first.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        hours_data = json.load(f)

    sections = to_convex_sections(hours_data)
    fetched_at_ms = int(time.time() * 1000)

    result = push_resort_hours(
        RESORT_ID,
        RESORT_NAME,
        SOURCE_URL,
        sections,
        fetched_at_ms=fetched_at_ms,
    )

    if result is not None:
        print("Pushed to Convex:", result)
    else:
        print("Convex not configured; nothing was pushed.")


if __name__ == "__main__":
    main()
