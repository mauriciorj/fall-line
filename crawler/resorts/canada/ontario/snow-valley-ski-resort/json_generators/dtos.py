from typing import Any


def to_hours(hours_data: dict[str, Any]) -> list[dict[str, Any]]:
    sections = []
    for section_name, section_value in hours_data.items():
        if not section_value:
            continue
        first_value = next(iter(section_value.values()))
        if isinstance(first_value, dict):
            sections.append({
                "name": section_name,
                "activities": [
                    {"name": activity, "hours": [{"day": day, "time": time} for day, time in days.items()]}
                    for activity, days in section_value.items()
                ],
            })
        else:
            sections.append({
                "name": section_name,
                "hours": [{"day": day, "time": time} for day, time in section_value.items()],
            })
    return sections


def to_rates_dto(rates: dict[str, Any]) -> dict[str, Any]:
    items = []
    for section_name, sections in rates.items():
        for section in sections:
            for category in section.get("categories", []):
                for item in category.get("items", []):
                    items.append({
                        "name": f"{section_name} | {category.get('category', '')} | {item.get('name', '')}",
                        "prices": [
                            {"label": "price", "value": item.get("price", "")},
                            {"label": "description", "value": item.get("description", "")},
                        ],
                    })
    return {"items": items}


def to_rentals_dto(rentals: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "sections": [
            {
                "name": section.get("title", ""),
                "items": [
                    {
                        "name": item.get("name", ""),
                        "prices": [
                            {"label": "price", "value": item.get("price", "")},
                            {"label": "description", "value": item.get("description", "")},
                        ],
                    }
                    for item in section.get("items", [])
                ],
            }
            for section in rentals
        ]
    }


def to_weather_dto(status: dict[str, Any]) -> dict[str, Any]:
    report = status.get("snow_report", {})
    conditions = {
        target: report[source]
        for source, target in {
            "temperature": "temperature",
            "base_depth": "baseDepth",
            "new_snow": "newSnow",
            "snow_surface": "surfaceConditions",
            "snowmaking": "snowmaking",
        }.items()
        if report.get(source) not in (None, "")
    }
    weather = {
        "lifts": status.get("lifts", []),
        "trails": status.get("runs", []),
        "tubing": status.get("tubing_zones", []),
        "rawData": status,
    }
    if conditions:
        weather["conditions"] = conditions
    for source, target in [("runs_summary", "trailsSummary"), ("lifts_summary", "liftsSummary"), ("tubing_summary", "tubingSummary")]:
        if status.get(source):
            weather[target] = status[source]
    return weather
