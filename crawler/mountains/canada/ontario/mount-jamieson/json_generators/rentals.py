import json
import os
import time

SOURCE_URL = "https://www.mountjamieson.ca/"
PAGE_URL = "https://www.mountjamieson.ca/service-shop-rentals"
RESORT_ID = "mount-jamieson"
RENTAL_PRICES = {
    "ski": {"adults": "$49.50", "youth": "$49.50"},
    "snowboard": {"adults": "$49.50", "youth": "$49.50"},
    "items": {"boots": "$25", "helmet": "$15", "poles": "$15"},
}


def get_rentals():
    return {category: values.copy() for category, values in RENTAL_PRICES.items()}


def main():
    payload = {"rentals": get_rentals(), "resortId": RESORT_ID, "sourceUrl": PAGE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "rentals.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
