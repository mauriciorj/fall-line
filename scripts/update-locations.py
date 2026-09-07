import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "crawler"))

from convex_client import call_query, push_locations


def normalize_locations(records):
    unique = {}
    for record in records:
        continent = (record.get("continent") or "").strip()
        country = (record.get("country") or "").strip()
        region = (record.get("region") or "Unknown").strip()
        if not continent or not country:
            continue

        key = (continent.casefold(), country.casefold(), region.casefold())
        unique[key] = {
            "continent": continent,
            "country": country,
            "region": region,
        }

    return sorted(
        unique.values(),
        key=lambda location: (
            location["continent"].casefold(),
            location["country"].casefold(),
            location["region"].casefold(),
        ),
    )


def main():
    records = call_query("resorts:listLocations", {})
    locations = normalize_locations(records)
    synced = push_locations(locations)
    print(f"Loaded {len(records)} resort records")
    print(f"Synchronized {int(synced)} unique locations")


if __name__ == "__main__":
    main()
