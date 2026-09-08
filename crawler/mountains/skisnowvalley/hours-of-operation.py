import json
import os
import sys
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

# Allow importing the shared Convex client from the parent directory.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from convex_client import push_resort_hours


RESORT_ID = "snow-valley-ski-resort"
SOURCE_URL = "https://www.skisnowvalley.com/about/"


def to_hours(hours_data):
    """
    Convert the nested hours dictionary into the normalized Convex hours shape.
    """
    normalized_hours = []
    for section_name, section_value in hours_data.items():
        if not section_value:
            continue

        first_val = next(iter(section_value.values()))

        if isinstance(first_val, dict):
            activities = []
            for activity_name, days in section_value.items():
                hours = [
                    {"day": day_name, "time": time}
                    for day_name, time in days.items()
                ]
                activities.append({"name": activity_name, "hours": hours})
            normalized_hours.append({"name": section_name, "activities": activities})
        else:
            hours = [
                {"day": day_name, "time": time}
                for day_name, time in section_value.items()
            ]
            normalized_hours.append({"name": section_name, "hours": hours})

    return normalized_hours


def get_hours_of_operation():
    """
    Crawl Snow Valley's about page to extract hours of operation.
    Returns a dictionary with the hours data organized by activity.
    """
    url = "https://www.skisnowvalley.com/about/"
    
    request_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=request_headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    hours_data = {}
    
    # Find all tables on the page
    tables = soup.find_all("table")
    
    for table in tables:
        # Get the section name from preceding heading
        prev_heading = table.find_previous(["h2", "h3", "h4"])
        section_name = prev_heading.get_text(strip=True) if prev_heading else "Hours"
        
        # Get column headers from thead
        thead = table.find("thead")
        if thead:
            header_cells = thead.find_all("th")
            column_headers = [cell.get_text(strip=True) for cell in header_cells]
        else:
            # Fallback: first row might be headers
            first_row = table.find("tr")
            if first_row:
                header_cells = first_row.find_all(["th", "td"])
                column_headers = [cell.get_text(strip=True) for cell in header_cells]
            else:
                column_headers = []
        
        # Process data rows from tbody or all tr elements
        tbody = table.find("tbody")
        rows = tbody.find_all("tr") if tbody else table.find_all("tr")
        
        # Handle tables without proper headers (simple day -> hours format)
        if not thead or len(column_headers) <= 2:
            if section_name not in hours_data:
                hours_data[section_name] = {}
            
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    day_name = cells[0].get_text(strip=True)
                    time = cells[1].get_text(strip=True)
                    hours_data[section_name][day_name] = time
            continue
        
        for row in rows:
            cells = row.find_all(["td", "th"])
            if not cells:
                continue
            
            # First cell is the day name
            day_name = cells[0].get_text(strip=True)
            
            # Remaining cells are hours for each activity
            for i, cell in enumerate(cells[1:], 1):
                if i < len(column_headers):
                    activity = column_headers[i]
                    time = cell.get_text(strip=True)
                    
                    # Create nested structure: section -> activity -> day -> hours
                    if section_name not in hours_data:
                        hours_data[section_name] = {}
                    
                    if activity not in hours_data[section_name]:
                        hours_data[section_name][activity] = {}
                    
                    hours_data[section_name][activity][day_name] = time
    
    return hours_data


def main():
    print("Fetching Snow Valley hours of operation...")
    hours = get_hours_of_operation()
    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(hours, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")

    hours = to_hours(hours)
    updated_at_ms = int(time.time() * 1000)
    push_resort_hours(
        RESORT_ID,
        SOURCE_URL,
        hours,
        updated_at_ms=updated_at_ms,
    )
    return hours


if __name__ == "__main__":
    main()
