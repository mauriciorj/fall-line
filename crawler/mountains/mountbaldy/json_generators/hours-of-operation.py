import json
import os
import time

SOURCE_URL = "https://www.skimountbaldy.ca/"
RESORT_ID = "mount-baldy"


def get_hours():
    return {"sunday": "10:00am to 5:00pm", "monday": "10:00am to 5:00pm", "tuesday": "10:00am to 5:00pm", "wednesday": "10:00am to 5:00pm", "thursday": "10:00am to 5:00pm", "friday": "10:00am to 5:00pm", "saturday": "10:00am to 5:00pm"}


def main():
    payload = {"hours": get_hours(), "resortId": RESORT_ID, "sourceUrl": SOURCE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
