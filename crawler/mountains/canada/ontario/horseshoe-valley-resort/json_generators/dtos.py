from typing import Any


def _row_to_item(row: Any) -> dict[str, Any]:
    if isinstance(row, dict):
        name_key = next(
            (
                key
                for key in row
                if key.lower() in {"name", "item", "package", "category"}
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


def to_hours(hours_data: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
    return [
        {
            "name": section_name,
            "hours": [
                {"day": day_name, "time": time}
                for day_name, time in days.items()
            ],
        }
        for section_name, days in hours_data.items()
        if days
    ]


def to_rates_dto(rates: dict[str, list[Any]] | list[Any]) -> dict[str, Any]:
    rows = rates.get("lift_tickets", []) if isinstance(rates, dict) else rates
    return {"items": [_row_to_item(row) for row in rows]}


def to_rentals_dto(rentals: dict[str, list[Any]] | list[Any]) -> dict[str, Any]:
    if isinstance(rentals, list):
        rentals = {"rentals": rentals}
    return {
        "sections": [
            {
                "name": section_name,
                "items": [_row_to_item(row) for row in rows],
            }
            for section_name, rows in rentals.items()
        ]
    }


def _run_dto(row: dict[str, Any], difficulty: str) -> dict[str, Any]:
    trail = {
        "name": row.get("name", ""),
        "status": row.get("day_status", ""),
    }
    if difficulty:
        trail["difficulty"] = difficulty
    if row.get("day_status") not in (None, ""):
        trail["dayStatus"] = row["day_status"]
    if row.get("night_status") not in (None, ""):
        trail["nightStatus"] = row["night_status"]
    return trail


def _lift_dto(row: dict[str, Any]) -> dict[str, Any]:
    lift = {
        "name": row.get("name", ""),
        "status": row.get("day_status", ""),
    }
    if row.get("day_status") not in (None, ""):
        lift["dayStatus"] = row["day_status"]
    if row.get("night_status") not in (None, ""):
        lift["nightStatus"] = row["night_status"]
    return lift


def to_weather_dto(status: dict[str, Any]) -> dict[str, Any]:
    condition_map = {
        "temperature": "temperature",
        "base_depth": "baseDepth",
        "new_snow": "newSnow",
        "snowfall_24h": "newSnow",
        "surface_conditions": "surfaceConditions",
        "snowmaking": "snowmaking",
        "hours": "hours",
    }
    conditions = {
        target: value
        for source, target in condition_map.items()
        for value in [status.get("conditions", {}).get(source)]
        if value not in (None, "")
    }

    trails = []
    terrain_parks = []
    for difficulty, rows in status.get("runs", {}).items():
        target = terrain_parks if difficulty == "terrain_park" else trails
        target.extend(_run_dto(row, difficulty) for row in rows)

    weather_data: dict[str, Any] = {
        "lifts": [_lift_dto(row) for row in status.get("lifts", [])],
        "trails": trails,
        "rawData": status,
    }
    if conditions:
        weather_data["conditions"] = conditions
    if terrain_parks:
        weather_data["terrainParks"] = terrain_parks

    cross_country = [
        {
            "trail": row.get("trail", ""),
            "distance": row.get("distance"),
            "status": row.get("open", ""),
            "trackSet": row.get("track_set"),
            "groomedToday": row.get("groomed_today"),
        }
        for row in status.get("cross_country", [])
    ]
    if cross_country:
        weather_data["crossCountry"] = cross_country

    tube_park = status.get("tube_park")
    if tube_park:
        weather_data["tubing"] = [
            {
                "name": "Tube Park",
                "status": tube_park.get("status", ""),
                "hours": tube_park.get("hours"),
            }
        ]

    for source, target in (
        ("lifts_summary", "liftsSummary"),
        ("trails_summary", "trailsSummary"),
    ):
        if status.get(source):
            weather_data[target] = status[source]
    return weather_data
