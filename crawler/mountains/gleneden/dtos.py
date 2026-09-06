from typing import Any


def _row_to_item(row: Any) -> dict[str, Any]:
    if isinstance(row, dict):
        name_key = next(
            (
                key
                for key in row
                if key.lower() in {"name", "item", "category", "description"}
            ),
            next(iter(row), "name"),
        )
        prices = [
            {"label": label, "value": value}
            for label, value in row.items()
            if label != name_key
        ]
        return {"name": row.get(name_key, ""), "prices": prices}

    if isinstance(row, list):
        return {
            "name": row[0] if row else "",
            "prices": [
                {"label": f"Column_{index}", "value": value}
                for index, value in enumerate(row[1:], 2)
            ],
        }

    return {"name": str(row), "prices": []}


def to_rates_dto(rates: dict[str, list[Any]] | list[Any]) -> dict[str, Any]:
    if isinstance(rates, dict):
        return {
            "sections": [
                {
                    "name": section_name,
                    "items": [_row_to_item(row) for row in rows],
                }
                for section_name, rows in rates.items()
            ]
        }

    return {"items": [_row_to_item(row) for row in rates]}


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


def _status_item(row: dict[str, Any]) -> dict[str, Any]:
    item = {
        "name": row.get("name", ""),
        "status": row.get("status", ""),
    }
    for source, target in {
        "difficulty": "difficulty",
        "day": "dayStatus",
        "night": "nightStatus",
        "number": "number",
    }.items():
        value = row.get(source)
        if value not in (None, ""):
            item[target] = value
    return item


def to_weather_dto(status: dict[str, Any]) -> dict[str, Any]:
    condition_map = {
        "temperature": "temperature",
        "base_depth": "baseDepth",
        "new_snow": "newSnow",
        "surface": "surfaceConditions",
        "surface_conditions": "surfaceConditions",
        "snow_condition": "surfaceConditions",
        "snowmaking": "snowmaking",
        "last_updated": "lastUpdated",
        "hours": "hours",
    }
    conditions = {
        target: value
        for source, target in condition_map.items()
        for value in [status.get("conditions", {}).get(source)]
        if value not in (None, "")
    }

    weather_data: dict[str, Any] = {
        "lifts": [_status_item(row) for row in status.get("lifts", [])],
        "trails": [_status_item(row) for row in status.get("trails", [])],
        "rawData": status,
    }
    if conditions:
        weather_data["conditions"] = conditions
    if status.get("lifts_summary"):
        weather_data["liftsSummary"] = status["lifts_summary"]
    if status.get("trails_summary"):
        weather_data["trailsSummary"] = status["trails_summary"]

    return weather_data
