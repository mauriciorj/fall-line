import time
from typing import Any


SOURCE = "skiresort.info"


def to_convex_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    fetched_at = int(time.time() * 1000)
    output = []

    for record in records:
        source_id = str(record.get("id", ""))
        location_trail = record.get("location", [])
        image_url = record.get("image_url")
        directory_data = {
            "locationTrail": location_trail,
            "url": record.get("url"),
            "rating": record.get("rating"),
            "altitudeDifference": record.get("altitude_difference"),
            "altitudeBase": record.get("altitude_base"),
            "altitudeTop": record.get("altitude_top"),
            "slopesTotal": record.get("slopes_total"),
            "slopesEasy": record.get("slopes_easy"),
            "slopesIntermediate": record.get("slopes_intermediate"),
            "slopesDifficult": record.get("slopes_difficult"),
            "skiPassPrice": record.get("ski_pass_price"),
            "imageUrl": image_url,
            "fetchedAt": fetched_at,
            "rawData": record,
        }
        normalized = {
            "source": SOURCE,
            "sourceId": f"{SOURCE.replace('.', '-')}-{source_id}",
            "name": record.get("name", ""),
            "continent": location_trail[0] if len(location_trail) > 0 else None,
            "country": location_trail[1] if len(location_trail) > 1 else None,
            "region": location_trail[2] if len(location_trail) > 2 else None,
            "address": ", ".join(location_trail),
            "website": record.get("url"),
            "image": image_url,
            "directoryData": {
                key: value
                for key, value in directory_data.items()
                if value is not None
            },
        }
        output.append(
            {
                key: value
                for key, value in normalized.items()
                if value is not None
            }
        )

    return output
