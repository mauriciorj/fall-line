from typing import Any


def _row_to_item(row: Any) -> dict[str, Any]:
    if not isinstance(row, dict):
        return {"name": str(row), "prices": []}

    name_key = next(
        (
            key
            for key in row
            if key.lower() in {"name", "item", "title", "category", "column_1"}
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


def _flatten_hours(name: str, value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, dict) or not value:
        return []

    direct_hours = [
        {"day": day, "time": time}
        for day, time in value.items()
        if not isinstance(time, dict) and time not in (None, "")
    ]
    result = [{"name": name, "hours": direct_hours}] if direct_hours else []

    for child_name, child_value in value.items():
        if isinstance(child_value, dict):
            result.extend(_flatten_hours(f"{name} | {child_name}", child_value))
    return result


def to_hours(hours: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for section_name, section in hours.items():
        result.extend(_flatten_hours(section_name, section))
    return result


def to_rates_dto(rates: dict[str, list[Any]]) -> dict[str, Any]:
    items = []
    for section_name, rows in rates.items():
        for row in rows:
            item = _row_to_item(row)
            item["name"] = f"{section_name} | {item['name']}"
            items.append(item)
    return {"items": items}


def to_rentals_dto(rentals: dict[str, Any]) -> dict[str, Any]:
    sections = []
    for section_name, value in rentals.items():
        rows = value if isinstance(value, list) else [value]
        items = [_row_to_item(row) for row in rows if isinstance(row, dict) and row]
        if items:
            sections.append({"name": section_name, "items": items})
    return {"sections": sections}


def to_weather_dto(status: dict[str, Any]) -> dict[str, Any]:
    trails = []
    terrain_parks = []
    for area, area_trails in status.get("trails", {}).items():
        for row in area_trails:
            trail = {
                "name": row.get("name", ""),
                "status": row.get("status", ""),
                "area": area,
            }
            if row.get("difficulty"):
                trail["difficulty"] = row["difficulty"]
            if "terrain park" in trail["name"].lower():
                terrain_parks.append(trail)
            else:
                trails.append(trail)

    lifts = [
        {
            "name": row.get("name", ""),
            "status": row.get("status", ""),
            **({"hours": row["hours"]} if row.get("hours") else {}),
        }
        for row in status.get("lifts", [])
    ]
    return {
        "lifts": lifts,
        "trails": trails,
        "terrainParks": terrain_parks,
        "rawData": status,
    }
