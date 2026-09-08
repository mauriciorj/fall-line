import json
import re
import os
import sys
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from convex_client import push_weather_and_status
from dtos import to_weather_dto

URL = "https://horseshoeresort.com/ski-report-trails/"
RESORT_ID = "horseshoe-valley-resort"


def get_trail_status():
    """
    Crawl Horseshoe Resort's ski report page to extract all conditions:
    - Snow/weather conditions
    - Alpine runs status
    - Chair lifts status
    - Cross-country trails status
    - Tube park status
    """
    url = URL
    
    request_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, headers=request_headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    data = {
        "conditions": {},
        "runs": {
            "easy": [],
            "difficult": [],
            "more_difficult": [],
            "terrain_park": []
        },
        "lifts": [],
        "cross_country": [],
        "tube_park": {}
    }
    
    # Extract snow/weather conditions from the conditions section
    # Look for the section containing Hours, Conditions, Base Depth
    conditions_section = soup.find(string=lambda s: s and "Base Depth" in s if s else False)
    if conditions_section:
        parent = conditions_section.find_parent()
        while parent and len(parent.get_text(strip=True)) < 200:
            parent = parent.find_parent()
        
        if parent:
            text = parent.get_text(separator="|", strip=True)
            
            # Extract Hours
            hours_match = re.search(r"Hours\|([^|]+)", text)
            if hours_match:
                data["conditions"]["hours"] = hours_match.group(1).strip()
            
            # Extract Conditions (surface)
            cond_match = re.search(r"Conditions\|([^|]+)", text)
            if cond_match and "°C" not in cond_match.group(1):
                data["conditions"]["surface_conditions"] = cond_match.group(1).strip()
            
            # Extract Base Depth
            base_match = re.search(r"Base Depth\|([^|]+)", text)
            if base_match:
                data["conditions"]["base_depth"] = base_match.group(1).strip()
    
    # Extract snowfall
    snowfall_el = soup.find(string=lambda s: s and "Snowfall" in s if s else False)
    if snowfall_el:
        parent = snowfall_el.find_parent()
        if parent:
            grandparent = parent.find_parent()
            if grandparent:
                text = grandparent.get_text(separator="|", strip=True)
                # Look for number followed by cm
                snow_match = re.search(r"(\d+)\s*\|?\s*cm", text)
                if snow_match:
                    data["conditions"]["snowfall_24h"] = f"{snow_match.group(1)} cm"
    
    # Extract tube park info
    tube_el = soup.find(string=lambda s: s and "Tube Park" in s if s else False)
    if tube_el:
        parent = tube_el.find_parent()
        if parent:
            container = parent.find_parent()
            while container and len(container.get_text(strip=True)) < 50:
                container = container.find_parent()
            if container:
                text = container.get_text(separator=" ", strip=True)
                # Extract hours - look for pattern like "Open 9AM-9PM - Tuesday to Saturday Open 9AM-5PM Sunday"
                hours_match = re.search(r"(Open\s+\d+[AP]M\s*-\s*\d+[AP]M.*?(?:Sunday|Saturday|Monday|Friday))", text, re.IGNORECASE)
                if hours_match:
                    data["tube_park"]["hours"] = hours_match.group(1).strip()
                else:
                    # Fallback
                    hours_text = text.replace("Tube Park", "").replace("Hours", "").strip()
                    data["tube_park"]["hours"] = hours_text[:80].strip() if hours_text else ""
                data["tube_park"]["status"] = "open" if "Open" in text else "closed"
    
    # Extract runs and lifts from tables
    tables = soup.find_all("table")
    
    for table in tables:
        rows = table.find_all("tr")
        if not rows:
            continue
        
        # Get header row to determine table type
        header_cells = rows[0].find_all(["th", "td"])
        headers = [cell.get_text(strip=True) for cell in header_cells]
        
        # Determine table type from first header
        first_header = headers[0].lower() if headers else ""
        
        # Check if this is a cross-country table
        if "trail" in first_header and "distance" in " ".join(headers).lower():
            for row in rows[1:]:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 5:
                    data["cross_country"].append({
                        "trail": cells[0].get_text(strip=True),
                        "distance": cells[1].get_text(strip=True),
                        "open": cells[2].get_text(strip=True),
                        "track_set": cells[3].get_text(strip=True),
                        "groomed_today": cells[4].get_text(strip=True)
                    })
            continue
        
        # Check if this is a lift table (no difficulty level in header)
        if first_header == "" or "carpet" in " ".join([r.get_text().lower() for r in rows]):
            # Check if it contains lift names
            has_lift = any("chair" in row.get_text().lower() or "carpet" in row.get_text().lower() or "express" in row.get_text().lower() for row in rows)
            if has_lift:
                for row in rows[1:]:
                    cells = row.find_all(["td", "th"])
                    if len(cells) >= 3:
                        data["lifts"].append({
                            "name": cells[0].get_text(strip=True),
                            "day_status": cells[1].get_text(strip=True),
                            "night_status": cells[2].get_text(strip=True)
                        })
                continue
        
        # Determine difficulty category
        difficulty_map = {
            "easy": "easy",
            "difficult": "difficult",
            "more difficult": "more_difficult",
            "terrain park": "terrain_park"
        }
        
        category = None
        for key, value in difficulty_map.items():
            if key in first_header.lower():
                category = value
                break
        
        if category:
            for row in rows[1:]:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 3:
                    data["runs"][category].append({
                        "name": cells[0].get_text(strip=True),
                        "day_status": cells[1].get_text(strip=True),
                        "night_status": cells[2].get_text(strip=True)
                    })
    
    return data


def main():
    print("Fetching Horseshoe Resort trail conditions...")
    status = get_trail_status()
    output_file = os.path.join(os.path.dirname(__file__), "weather-and-status.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")

    result = push_weather_and_status(
        RESORT_ID,
        URL,
        to_weather_dto(status),
        updated_at_ms=int(time.time() * 1000),
    )
    if result is not None:
        print("Pushed to Convex:", result)

    return status


if __name__ == "__main__":
    main()
