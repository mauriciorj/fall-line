import json
import time
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from convex_client import push_weather_and_status
from dtos import to_weather_dto

URL = "https://www.discoverchicopee.com/activity-report"
RESORT_ID = "chicopee"
RESORT_NAME = "Chicopee"


def get_trail_status():
    """
    Crawl Chicopee's activity report page to extract trail and lift status.
    Uses Selenium because the page is rendered with JavaScript.
    """
    url = URL
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(url)
        # Wait for the page to load dynamic content
        time.sleep(5)
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        data = {
            "lifts": [],
            "trails": [],
            "terrain_parks": [],
            "conditions": {}
        }
        
        # Look for status indicators - Chicopee uses various class patterns
        # Find all elements that might contain trail/lift info
        
        # Try to find lift status sections
        lift_sections = soup.find_all(class_=lambda x: x and ("lift" in str(x).lower() or "chair" in str(x).lower()) if x else False)
        for section in lift_sections:
            text = section.get_text(separator="|", strip=True)
            if text:
                parts = text.split("|")
                if len(parts) >= 1:
                    status = "open" if any(s in text.lower() for s in ["open", "✓", "yes"]) else "closed"
                    data["lifts"].append({
                        "name": parts[0],
                        "status": status
                    })
        
        # Try to find trail status sections
        trail_sections = soup.find_all(class_=lambda x: x and ("trail" in str(x).lower() or "run" in str(x).lower() or "slope" in str(x).lower()) if x else False)
        for section in trail_sections:
            text = section.get_text(separator="|", strip=True)
            if text:
                parts = text.split("|")
                if len(parts) >= 1:
                    status = "open" if any(s in text.lower() for s in ["open", "✓", "yes"]) else "closed"
                    data["trails"].append({
                        "name": parts[0],
                        "status": status
                    })
        
        # Try to find terrain park sections
        park_sections = soup.find_all(class_=lambda x: x and ("park" in str(x).lower() or "terrain" in str(x).lower()) if x else False)
        for section in park_sections:
            text = section.get_text(separator="|", strip=True)
            if text:
                parts = text.split("|")
                if len(parts) >= 1:
                    status = "open" if any(s in text.lower() for s in ["open", "✓", "yes"]) else "closed"
                    data["terrain_parks"].append({
                        "name": parts[0],
                        "status": status
                    })
        
        # Alternative: Look for tables which often contain status info
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows[1:]:  # Skip header
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    name = cells[0].get_text(strip=True)
                    status_text = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                    status = "open" if any(s in status_text.lower() for s in ["open", "✓", "yes"]) else "closed"
                    data["trails"].append({
                        "name": name,
                        "status": status
                    })
        
        # Alternative: Look for list items with status indicators
        list_items = soup.find_all("li")
        for item in list_items:
            # Check if this looks like a trail/lift status item
            text = item.get_text(strip=True)
            classes = item.get("class", [])
            class_str = " ".join(classes) if classes else ""
            
            if any(keyword in class_str.lower() for keyword in ["status", "trail", "lift", "run"]):
                status = "open" if any(s in text.lower() for s in ["open", "✓", "yes"]) else "closed"
                data["trails"].append({
                    "name": text.split()[0] if text else "",
                    "status": status
                })
        
        # Look for divs with status-related content
        status_divs = soup.find_all("div", class_=lambda x: x and any(k in str(x).lower() for k in ["status", "report", "condition"]) if x else False)
        for div in status_divs:
            # Extract any structured data
            items = div.find_all(["div", "span", "p"])
            for item in items:
                text = item.get_text(strip=True)
                if text and len(text) < 100:  # Reasonable length for a status item
                    if "open" in text.lower() or "closed" in text.lower():
                        status = "open" if "open" in text.lower() else "closed"
                        name = text.replace("Open", "").replace("Closed", "").replace("open", "").replace("closed", "").strip()
                        if name:
                            data["trails"].append({
                                "name": name,
                                "status": status
                            })
        
        # Remove duplicates
        seen_lifts = set()
        unique_lifts = []
        for lift in data["lifts"]:
            if lift["name"] not in seen_lifts and lift["name"]:
                seen_lifts.add(lift["name"])
                unique_lifts.append(lift)
        data["lifts"] = unique_lifts
        
        seen_trails = set()
        unique_trails = []
        for trail in data["trails"]:
            if trail["name"] not in seen_trails and trail["name"]:
                seen_trails.add(trail["name"])
                unique_trails.append(trail)
        data["trails"] = unique_trails
        
        seen_parks = set()
        unique_parks = []
        for park in data["terrain_parks"]:
            if park["name"] not in seen_parks and park["name"]:
                seen_parks.add(park["name"])
                unique_parks.append(park)
        data["terrain_parks"] = unique_parks
        
        # Add summary
        data["lifts_summary"] = {
            "open": sum(1 for l in data["lifts"] if l["status"] == "open"),
            "total": len(data["lifts"])
        }
        data["trails_summary"] = {
            "open": sum(1 for t in data["trails"] if t["status"] == "open"),
            "total": len(data["trails"])
        }
        data["parks_summary"] = {
            "open": sum(1 for p in data["terrain_parks"] if p["status"] == "open"),
            "total": len(data["terrain_parks"])
        }
        
        return data
        
    finally:
        driver.quit()


def main():
    print("Fetching Chicopee trail status...")
    status = get_trail_status()
    output_file = os.path.join(os.path.dirname(__file__), "weather-and-status.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")

    result = push_weather_and_status(
        RESORT_ID,
        RESORT_NAME,
        URL,
        to_weather_dto(status),
        fetched_at_ms=int(time.time() * 1000),
    )
    if result is not None:
        print("Pushed to Convex:", result)

    return status


if __name__ == "__main__":
    main()
