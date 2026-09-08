from typing import Any


RESORT_ID_PREFIX = "skiresort-info-"


def to_convex_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output = []

    for record in records:
        external_id = str(record.get("id", "")).strip()
        location_trail = record.get("location", [])
        if not isinstance(location_trail, list):
            location_trail = []

        normalized = {
            "resortId": f"{RESORT_ID_PREFIX}{external_id}",
            "name": record.get("name", ""),
            "continent": location_trail[0] if len(location_trail) > 0 else None,
            "country": location_trail[1] if len(location_trail) > 1 else None,
            "region": location_trail[2] if len(location_trail) > 2 else None,
            "address": ", ".join(location_trail),
            "website": record.get("url"),
            "image": record.get("image_url"),
        }

        rating = record.get("rating")
        if isinstance(rating, (int, float)):
            normalized["rating"] = rating

        output.append(
            {
                key: value
                for key, value in normalized.items()
                if value is not None
            }
        )

    return output
