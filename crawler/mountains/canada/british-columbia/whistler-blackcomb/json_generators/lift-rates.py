import json
import os
import time

RESORT_ID = "whistler-blackcomb"
SOURCE_URL = "https://waitingroom.snow.com/?c=vailresorts&e=vailresortsecomm1&ver=v3-aspnet-3.6.2&cver=149&man=Sapphire%20-%20All%20Non%20Reservation%20Pages%20and%20APIs%20-%20PROD&t=https%3A%2F%2Fwww.whistlerblackcomb.com%2Fplan-your-trip%2Flift-access%2Ftickets.aspx"


def get_lift_rates():
    return {}


def main():
    payload = {
        "rates": get_lift_rates(),
        "resortId": RESORT_ID,
        "sourceUrl": SOURCE_URL,
        "updatedAt": int(time.time() * 1000),
    }
    output_file = os.path.join(os.path.dirname(__file__), "lift-rates.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
