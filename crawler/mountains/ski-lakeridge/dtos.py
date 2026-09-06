from typing import Any


def _row_to_item(row: Any) -> dict[str, Any]:
    if isinstance(row, dict):
        name_key = next(
            (
                key
                for key in row
                if key.lower() in {"name", "item", "category", "description", "time"}
            ),
            next(iter(row), "name"),
        )
        prices = [
            {"label": label, "value": value}
            for label, value in row.items()
            if label != name_key
        ]
        return {"name": row.get(name_key, ""), "prices": prices}

    return {"name": str(row), "prices": []}


def to_hours_sections(hours: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    sections = []
    for section_name, rows in hours.items():
        hour_rows = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            day = row.get("Date of operation", "")
            time = row.get("Hours of operation", "")
            if day or time:
                hour_rows.append({"day": day, "time": time})
        sections.append({"name": section_name, "hours": hour_rows})
    return sections


def to_rates_dto(rates: dict[str, list[Any]]) -> dict[str, Any]:
    return {
        "sections": [
            {
                "name": section_name,
                "items": [_row_to_item(row) for row in rows],
            }
            for section_name, rows in rates.items()
        ]
    }


def to_rentals_dto(rentals: dict[str, list[Any]]) -> dict[str, Any]:
    return {
        "sections": [
            {
                "name": section_name,
                "items": [_row_to_item(row) for row in rows],
            }
            for section_name, rows in rentals.items()
        ]
    }


def to_weather_dto(trails: list[dict[str, Any]]) -> dict[str, Any]:
    normalized_trails = []
    terrain_parks = []
    tubing = []

    for row in trails:
        name = row.get("name", "")
        item = {
            "name": name,
            "status": row.get("status", ""),
        }
        if row.get("difficulty"):
            item["difficulty"] = row["difficulty"]

        name_lower = name.lower()
        if "tube park" in name_lower:
            tubing.append({"name": name, "status": row.get("status", "")})
        elif "terrain park" in name_lower or "snowcross" in name_lower:
            terrain_parks.append(item)
        else:
            normalized_trails.append(item)

    return {
        "lifts": [],
        "trails": normalized_trails,
        "terrainParks": terrain_parks,
        "tubing": tubing,
        "trailsSummary": {
            "open": sum(
                1 for trail in normalized_trails
                if trail["status"].lower() == "open"
            ),
            "total": len(normalized_trails),
        },
        "rawData": trails,
    }
