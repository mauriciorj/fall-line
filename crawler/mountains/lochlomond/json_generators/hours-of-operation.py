import json
import os
import time

SOURCE_URL = "https://www.lochlomond.ca/"
PAGE_URL = "https://www.lochlomond.ca/hill-hours/"
RESORT_ID = "loch-lomond"


def get_hours():
    return {"sunday": "10am to 6pm", "monday": "closed", "tuesday": "closed", "wednesday": "closed", "thursday": "closed", "friday": "10am to 8pm", "saturday": "10am to 8pm"}


def main():
    payload = {"hours": get_hours(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
