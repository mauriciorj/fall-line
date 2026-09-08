from typing import Any


def _row_to_item(row: Any) -> dict[str, Any]:
    if isinstance(row, dict):
        name_key = next(
            (
                key
                for key in row
                if key.lower() in {"name", "item", "category", "ticket", "rental"}
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


def to_hours(hours: dict[str, str]) -> list[dict[str, Any]]:
    return [
        {
            "name": "Hours of operation",
            "hours": [
                {"day": day, "time": time}
                for day, time in hours.items()
            ],
        }
    ] if hours else []


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


def _lift_dto(row: dict[str, Any]) -> dict[str, Any]:
    lift = {
        "name": row.get("name", ""),
        "status": row.get("status", ""),
    }
    if row.get("letter"):
        lift["identifier"] = row["letter"]
    return lift


def _trail_dto(row: dict[str, Any]) -> dict[str, Any]:
    trail = {
        "name": row.get("name", ""),
        "status": row.get("status", ""),
    }
    if row.get("difficulty"):
        trail["difficulty"] = row["difficulty"]
    return trail


def to_weather_dto(status: dict[str, Any]) -> dict[str, Any]:
    condition_map = {
        "Snow Base": "baseDepth",
        "New Snow": "newSnow",
        "Conditions": "surfaceConditions",
    }
    daily_conditions = status.get("Daily Conditions", {})
    conditions = {
        target: value
        for source, target in condition_map.items()
        for value in [daily_conditions.get(source)]
        if value not in (None, "")
    }

    trails = []
    terrain_parks = []
    for row in status.get("Runs", []):
        target = terrain_parks if row.get("difficulty") == "Terrain Park" else trails
        target.append(_trail_dto(row))

    weather_data: dict[str, Any] = {
        "lifts": [_lift_dto(row) for row in status.get("Lifts", [])],
        "trails": trails,
        "rawData": status,
        "trailsSummary": {
            "open": sum(1 for row in trails if row["status"].lower() == "open"),
            "total": len(trails),
        },
        "liftsSummary": {
            "open": sum(1 for row in status.get("Lifts", []) if row.get("status", "").lower() == "open"),
            "total": len(status.get("Lifts", [])),
        },
    }
    if conditions:
        weather_data["conditions"] = conditions
    if terrain_parks:
        weather_data["terrainParks"] = terrain_parks

    return weather_data
