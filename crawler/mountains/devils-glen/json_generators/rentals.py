import json
import os
import time

SOURCE_URL = "https://www.devilsglen.com"
PAGE_URL = f"{SOURCE_URL}/About/Rental_Equipment"
RESORT_ID = "devils-glen"


def main():
    payload = {
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
