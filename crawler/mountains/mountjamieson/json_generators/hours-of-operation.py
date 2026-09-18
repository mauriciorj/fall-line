import json
import os
import time

SOURCE_URL = "https://www.mountjamieson.ca/"
PAGE_URL = "https://www.mountjamieson.ca/"
RESORT_ID = "mount-jamieson"


def get_hours():
    return {"sunday": "10:00am to 4:30pm", "monday": "closed", "tuesday": "10:00am to 3:30pm", "wednesday": "10:00am to 3:30pm", "thursday": "10:00am to 3:30pm", "friday": "10:00am to 3:30pm", "saturday": "10:00am to 4:30pm"}


def main():
    payload = {"hours": get_hours(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
