import json
import os
import time

PAGE_URL = "https://www.batawaskihill.com/ski-snowboard-rentals"
RESORT_ID = "batawa-ski-hill"


def get_rentals():
    return {"ski": {}, "snowboard": {}, "items": {}}


def main():
    payload = {
        "rentals": get_rentals(),
        "resortId": RESORT_ID,
        "sourceUrl": PAGE_URL,
        "updatedAt": int(time.time() * 1000),
    }
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
