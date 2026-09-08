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
        return {
            "name": row.get(name_key, ""),
            "prices": [
                {"label": label, "value": value}
                for label, value in row.items()
                if label != name_key and value not in (None, "")
            ],
        }
    return {"name": str(row), "prices": []}


def to_hours(hours: dict[str, str]) -> list[dict[str, Any]]:
    return [
        {
            "name": "Hours of operation",
            "hours": [{"day": day, "time": time} for day, time in hours.items()],
        }
    ] if hours else []


def to_rates_dto(rates: dict[str, list[Any]]) -> dict[str, Any]:
    items = []
    for section_name, rows in rates.items():
        for row in rows:
            item = _row_to_item(row)
            item["name"] = f"{section_name} | {item['name']}"
            items.append(item)
    return {"items": items}


def to_rentals_dto(rentals: dict[str, list[Any]]) -> dict[str, Any]:
    return {
        "sections": [
            {"name": section_name, "items": [_row_to_item(row) for row in rows]}
            for section_name, rows in rentals.items()
        ]
    }


def _lift_dto(row: dict[str, Any]) -> dict[str, Any]:
    item = {"name": row.get("name", ""), "status": row.get("status", "")}
    if row.get("letter"):
        item["identifier"] = row["letter"]
    return item


def _trail_dto(row: dict[str, Any]) -> dict[str, Any]:
    item = {"name": row.get("name", ""), "status": row.get("status", "")}
    if row.get("difficulty"):
        item["difficulty"] = row["difficulty"]
    return item


def to_weather_dto(status: dict[str, Any]) -> dict[str, Any]:
    condition_map = {"Snow Base": "baseDepth", "New Snow": "newSnow", "Conditions": "surfaceConditions"}
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
            "open": sum(row["status"].lower() == "open" for row in trails),
            "total": len(trails),
        },
        "liftsSummary": {
            "open": sum(row.get("status", "").lower() == "open" for row in status.get("Lifts", [])),
            "total": len(status.get("Lifts", [])),
        },
    }
    if conditions:
        weather_data["conditions"] = conditions
    if terrain_parks:
        weather_data["terrainParks"] = terrain_parks
    return weather_data
