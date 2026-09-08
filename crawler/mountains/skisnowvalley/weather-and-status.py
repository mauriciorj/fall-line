import json
import os
import re
import sys
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from convex_client import push_weather_and_status


RESORT_ID = "snow-valley-ski-resort"
SOURCE_URL = "https://www.skisnowvalley.com/plan/weather-webcams/"


def get_trails_status():
    """
    Crawl Snow Valley's weather/webcams page to extract snow conditions,
    lift status, trail status, and tubing conditions.
    """
    url = SOURCE_URL
    
    request_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, headers=request_headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    data = {
        "snow_report": {},
        "runs": [],
        "lifts": [],
        "tubing_zones": []
    }
    
    # Extract snow report from the first table
    tables = soup.find_all("table")
    if tables:
        for row in tables[0].find_all("tr"):
            cells = row.find_all(["td", "th"])
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                # Normalize key to snake_case
                key_normalized = key.lower().replace(" ", "_")
                data["snow_report"][key_normalized] = value
    
    # Extract runs (trails)
    runs_headings = soup.find_all(string=re.compile(r"^Runs$"))
    for heading in runs_headings:
        parent = heading.find_parent()
        if parent:
            container = parent.find_parent()
            while container and len(container.get_text(strip=True)) < 100:
                container = container.find_parent()
            
            if container:
                text_parts = container.get_text(separator="|", strip=True).split("|")
                # Parse: Runs|20/21 open|trail1|trail2|...
                i = 0
                while i < len(text_parts):
                    if text_parts[i] == "Runs" and i + 1 < len(text_parts):
                        # Get the open count
                        open_match = re.match(r"(\d+)/(\d+)\s*open", text_parts[i + 1])
                        if open_match:
                            # Get trail names after the count
                            j = i + 2
                            while j < len(text_parts) and text_parts[j] != "Runs":
                                trail_name = text_parts[j].strip()
                                if trail_name and trail_name not in [t["name"] for t in data["runs"]]:
                                    data["runs"].append({
                                        "name": trail_name,
                                        "status": "open"
                                    })
                                j += 1
                            i = j
                            continue
                    i += 1
                break
    
    # Extract open count for runs
    open_pattern = re.compile(r"(\d+)/(\d+)\s*open", re.IGNORECASE)
    runs_open_match = None
    for text in soup.find_all(string=open_pattern):
        parent_text = text.find_parent().find_parent().get_text(strip=True) if text.find_parent() else ""
        if "Runs" in parent_text:
            runs_open_match = open_pattern.search(text)
            if runs_open_match:
                data["runs_summary"] = {
                    "open": int(runs_open_match.group(1)),
                    "total": int(runs_open_match.group(2))
                }
                break
    
    # Extract lifts
    lifts_headings = soup.find_all(string=re.compile(r"^Lifts$"))
    for heading in lifts_headings[:1]:
        parent = heading.find_parent()
        if parent:
            container = parent.find_parent()
            while container and len(container.get_text(strip=True)) < 50:
                container = container.find_parent()
            
            if container:
                text_parts = container.get_text(separator="|", strip=True).split("|")
                # Parse: Lifts|6/8 open|lift1|lift2|...
                for i, part in enumerate(text_parts):
                    if part == "Lifts" and i + 1 < len(text_parts):
                        open_match = re.match(r"(\d+)/(\d+)\s*open", text_parts[i + 1])
                        if open_match:
                            data["lifts_summary"] = {
                                "open": int(open_match.group(1)),
                                "total": int(open_match.group(2))
                            }
                            # Get lift names
                            for j in range(i + 2, len(text_parts)):
                                lift_name = text_parts[j].strip()
                                if lift_name and not re.match(r"\d+/\d+", lift_name):
                                    data["lifts"].append({
                                        "name": lift_name,
                                        "status": "open"
                                    })
                        break
                break
    
    # Extract tubing zones
    tubing_headings = soup.find_all(string=re.compile(r"Tubing Zones"))
    for heading in tubing_headings[:1]:
        parent = heading.find_parent()
        if parent:
            container = parent.find_parent()
            while container and len(container.get_text(strip=True)) < 50:
                container = container.find_parent()
            
            if container:
                text_parts = container.get_text(separator="|", strip=True).split("|")
                # Parse: Tubing Zones|4/4 open|zone1|zone2|...
                i = 0
                while i < len(text_parts):
                    if "Tubing Zones" in text_parts[i] and i + 1 < len(text_parts):
                        open_match = re.match(r"(\d+)/(\d+)\s*open", text_parts[i + 1])
                        if open_match:
                            if "tubing_summary" not in data:
                                data["tubing_summary"] = {
                                    "open": int(open_match.group(1)),
                                    "total": int(open_match.group(2))
                                }
                            # Get zone names
                            j = i + 2
                            while j < len(text_parts) and "Tubing" not in text_parts[j]:
                                zone_name = text_parts[j].strip()
                                if zone_name and zone_name not in [z["name"] for z in data["tubing_zones"]]:
                                    data["tubing_zones"].append({
                                        "name": zone_name,
                                        "status": "open"
                                    })
                                j += 1
                            i = j
                            continue
                    i += 1
                break
    
    return data


def to_convex_weather(status):
    report = status.get("snow_report", {})
    field_map = {
        "temperature": "temperature",
        "base_depth": "baseDepth",
        "new_snow": "newSnow",
        "surface_conditions": "surfaceConditions",
        "snowmaking": "snowmaking",
        "last_updated": "lastUpdated",
        "hours": "hours",
    }
    conditions = {
        target: report[source]
        for source, target in field_map.items()
        if report.get(source) not in (None, "")
    }

    tubing = []
    for zone in status.get("tubing_zones", []):
        tubing_zone = {"status": zone.get("status", "")}
        if zone.get("name"):
            tubing_zone["name"] = zone["name"]
        tubing.append(tubing_zone)

    weather_data = {
        "lifts": status.get("lifts", []),
        "trails": status.get("runs", []),
        "tubing": tubing,
        "rawData": status,
    }
    if conditions:
        weather_data["conditions"] = conditions

    summaries = {
        "runs_summary": "trailsSummary",
        "lifts_summary": "liftsSummary",
        "tubing_summary": "tubingSummary",
    }
    for source, target in summaries.items():
        if status.get(source):
            weather_data[target] = status[source]

    return weather_data


def main():
    print("Fetching Snow Valley trails and conditions status...")
    status = get_trails_status()
    output_file = os.path.join(os.path.dirname(__file__), "weather-and-status.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")

    result = push_weather_and_status(
        RESORT_ID,
        SOURCE_URL,
        to_convex_weather(status),
        updated_at_ms=int(time.time() * 1000),
    )
    if result is not None:
        print("Pushed to Convex:", result)

    return status


if __name__ == "__main__":
    main()
