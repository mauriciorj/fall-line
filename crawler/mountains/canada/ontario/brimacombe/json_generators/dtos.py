from typing import Any


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


def to_rates_dto(rates: list[dict[str, str]]) -> dict[str, Any]:
    items = []
    for row in rates:
        if not isinstance(row, dict):
            items.append({"name": str(row), "prices": []})
            continue

        name = row.get("Age Categories", "")
        prices = [
            {"label": label, "value": value}
            for label, value in row.items()
            if label != "Age Categories"
        ]
        items.append({"name": name, "prices": prices})

    return {"items": items}


def to_rentals_dto(rentals: dict[str, list[dict[str, str]]]) -> dict[str, Any]:
    sections = []
    for section_name, rows in rentals.items():
        items = []
        for row in rows:
            if not isinstance(row, dict) or not row:
                continue

            name_key = next(
                (
                    key
                    for key in row
                    if key.lower() in {"name", "item"}
                    or "package" in key.lower()
                    or "rental item" in key.lower()
                ),
                next(iter(row)),
            )
            prices = [
                {"label": label, "value": value}
                for label, value in row.items()
                if label != name_key
            ]
            items.append({"name": row.get(name_key, ""), "prices": prices})

        sections.append({"name": section_name, "items": items})

    return {"sections": sections}


def _trail_dto(row: dict[str, str], identifier_key: str) -> dict[str, str]:
    trail = {
        "name": row.get("name", ""),
        "status": row.get("day", ""),
    }
    field_map = {
        "difficulty": "difficulty",
        "day": "dayStatus",
        "night": "nightStatus",
        identifier_key: "number",
    }
    for source, target in field_map.items():
        value = row.get(source)
        if value not in (None, ""):
            trail[target] = value
    return trail


def _lift_dto(row: dict[str, str]) -> dict[str, str]:
    lift = {
        "name": row.get("name", ""),
        "status": row.get("day", ""),
    }
    for source, target in {
        "day": "dayStatus",
        "night": "nightStatus",
        "letter": "identifier",
    }.items():
        value = row.get(source)
        if value not in (None, ""):
            lift[target] = value
    return lift


def to_weather_dto(status: dict[str, Any]) -> dict[str, Any]:
    weather_data: dict[str, Any] = {
        "lifts": [_lift_dto(row) for row in status.get("Lifts", [])],
        "trails": [
            _trail_dto(row, "number") for row in status.get("Trails", [])
        ],
        "rawData": status,
    }

    parks = status.get("Parks")
    if parks is not None:
        weather_data["terrainParks"] = [
            _trail_dto(row, "code") for row in parks
        ]

    return weather_data
