import json
import time
import re
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


def get_trail_status():
    """
    Crawl Blue Mountain's mountain report page to extract trail and lift status.
    Uses Selenium because the page is rendered with JavaScript.
    """
    url = "https://www.bluemountain.ca/mountain/mountain-report"
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(url)
        # Wait for the page to load
        time.sleep(5)
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        data = {
            "conditions": {},
            "lifts": [],
            "trails": {
                "orchard": [],
                "south": [],
                "village": [],
                "valley": [],
                "north": []
            }
        }
        
        # Extract weather/conditions
        weather_elements = soup.find_all(class_=lambda x: x and "WeatherWidget" in str(x) if x else False)
        for el in weather_elements:
            text = el.get_text(separator="|", strip=True)
            # Look for temperature, snow conditions
            temp_match = re.search(r"(-?\d+)\s*°", text)
            if temp_match:
                data["conditions"]["temperature"] = f"{temp_match.group(1)}°C"
        
        # Extract last updated time
        updated_el = soup.find(string=lambda s: s and "Updated" in s if s else False)
        if updated_el:
            data["conditions"]["last_updated"] = updated_el.strip()
        
        # Extract lifts
        lift_items = soup.find_all(class_=lambda x: x and "Lift_lift__" in str(x) if x else False)
        for lift in lift_items:
            text_parts = lift.get_text(separator="|", strip=True).split("|")
            if len(text_parts) >= 3:
                lift_data = {
                    "name": text_parts[0],
                    "hours": text_parts[1] if len(text_parts) > 1 else "",
                    "status": text_parts[2] if len(text_parts) > 2 else ""
                }
                data["lifts"].append(lift_data)
        
        # Extract trails by area
        # Find accordion sections for each area
        accordions = soup.find_all(class_=lambda x: x and "Accordion_accordion__" in str(x) if x else False)
        
        current_area = None
        area_mapping = {
            "orchard": "orchard",
            "south": "south",
            "village": "village",
            "valley": "valley",
            "north": "north"
        }
        
        for accordion in accordions:
            # Get area name from accordion title
            title_el = accordion.find(class_=lambda x: x and "accordionTitle" in str(x) if x else False)
            if title_el:
                area_name = title_el.get_text(strip=True).lower()
                for key in area_mapping:
                    if key in area_name:
                        current_area = area_mapping[key]
                        break
            
            # Get trails in this accordion
            trail_list = accordion.find(class_=lambda x: x and "trailList" in str(x) if x else False)
            if trail_list and current_area:
                trail_items = trail_list.find_all(recursive=False)
                for trail in trail_items:
                    text_parts = trail.get_text(separator="|", strip=True).split("|")
                    if len(text_parts) >= 2:
                        trail_data = {
                            "name": text_parts[0],
                            "status": text_parts[1] if len(text_parts) > 1 else ""
                        }
                        data["trails"][current_area].append(trail_data)
        
        # If no trails found via accordions, try alternative method
        if all(len(trails) == 0 for trails in data["trails"].values()):
            trail_lists = soup.find_all(class_=lambda x: x and "trailList" in str(x) if x else False)
            all_trails = []
            for tl in trail_lists:
                children = tl.find_all(recursive=False)
                for child in children:
                    text_parts = child.get_text(separator="|", strip=True).split("|")
                    if len(text_parts) >= 2:
                        all_trails.append({
                            "name": text_parts[0],
                            "status": text_parts[1]
                        })
            data["trails"]["all"] = all_trails
        
        # Count open/closed
        total_lifts = len(data["lifts"])
        open_lifts = sum(1 for l in data["lifts"] if "open" in l.get("status", "").lower())
        data["lifts_summary"] = {"open": open_lifts, "total": total_lifts}
        
        total_trails = sum(len(trails) for trails in data["trails"].values())
        open_trails = sum(
            1 for trails in data["trails"].values() 
            for t in trails if "open" in t.get("status", "").lower()
        )
        data["trails_summary"] = {"open": open_trails, "total": total_trails}
        
        return data
        
    finally:
        driver.quit()


def main():
    print("Fetching Blue Mountain trail status...")
    status = get_trail_status()
    output_file = os.path.join(os.path.dirname(__file__), "weather-and-status.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")
    return status


if __name__ == "__main__":
    main()
