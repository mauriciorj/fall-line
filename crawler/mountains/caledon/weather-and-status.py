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
    Crawl Caledon Ski Club's private-lessons page to extract Snow Conditions and Trail Status.
    Uses Selenium because the page is rendered with JavaScript.
    """
    url = "https://caledonskiclub.com/private-lessons"
    
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
            "snow_conditions": {},
            "trails": [],
            "lifts": []
        }
        
        # Look for Snow Conditions section
        # Try to find by heading text
        snow_heading = soup.find(string=re.compile(r"Snow\s*Conditions", re.IGNORECASE))
        if snow_heading:
            parent = snow_heading.find_parent()
            if parent:
                # Get the container/section that holds snow conditions
                section = parent.find_parent(["div", "section"])
                if section:
                    # Extract text content from the section
                    items = section.find_all(["p", "span", "div", "li"])
                    for item in items:
                        text = item.get_text(strip=True)
                        if text and len(text) < 200:
                            # Parse common snow condition fields
                            if re.search(r"base|depth", text, re.IGNORECASE):
                                data["snow_conditions"]["base_depth"] = text
                            elif re.search(r"new\s*snow|fresh", text, re.IGNORECASE):
                                data["snow_conditions"]["new_snow"] = text
                            elif re.search(r"surface|condition", text, re.IGNORECASE):
                                data["snow_conditions"]["surface"] = text
                            elif re.search(r"temp|temperature|°", text, re.IGNORECASE):
                                data["snow_conditions"]["temperature"] = text
                            elif re.search(r"last\s*updated|updated", text, re.IGNORECASE):
                                data["snow_conditions"]["last_updated"] = text
        
        # Look for Trail Status section
        trail_heading = soup.find(string=re.compile(r"Trail\s*Status", re.IGNORECASE))
        if trail_heading:
            parent = trail_heading.find_parent()
            if parent:
                section = parent.find_parent(["div", "section"])
                if section:
                    # Look for trail items - could be in tables, lists, or divs
                    # Try tables first
                    tables = section.find_all("table")
                    for table in tables:
                        rows = table.find_all("tr")
                        for row in rows:
                            cells = row.find_all(["td", "th"])
                            if len(cells) >= 2:
                                name = cells[0].get_text(strip=True)
                                status_text = cells[1].get_text(strip=True)
                                if name and name.lower() not in ["trail", "name", "status"]:
                                    status = "open" if any(s in status_text.lower() for s in ["open", "✓", "yes", "●"]) else "closed"
                                    data["trails"].append({
                                        "name": name,
                                        "status": status,
                                        "status_text": status_text
                                    })
                    
                    # Try list items
                    if not data["trails"]:
                        list_items = section.find_all("li")
                        for item in list_items:
                            text = item.get_text(strip=True)
                            if text:
                                status = "open" if any(s in text.lower() for s in ["open", "✓", "yes"]) else "closed"
                                data["trails"].append({
                                    "name": text,
                                    "status": status
                                })
        
        # Alternative: Search for status indicators anywhere on the page
        if not data["trails"]:
            # Look for elements with status-related classes
            status_elements = soup.find_all(class_=lambda x: x and any(k in str(x).lower() for k in ["trail", "run", "slope", "status"]) if x else False)
            for el in status_elements:
                text = el.get_text(strip=True)
                if text and len(text) < 100:
                    status = "open" if any(s in text.lower() for s in ["open", "✓", "yes"]) else "closed"
                    data["trails"].append({
                        "name": text,
                        "status": status
                    })
        
        # Look for lift status
        lift_heading = soup.find(string=re.compile(r"Lift\s*Status|Lifts", re.IGNORECASE))
        if lift_heading:
            parent = lift_heading.find_parent()
            if parent:
                section = parent.find_parent(["div", "section"])
                if section:
                    items = section.find_all(["li", "tr", "div"])
                    for item in items:
                        text = item.get_text(strip=True)
                        if text and len(text) < 100:
                            status = "open" if any(s in text.lower() for s in ["open", "✓", "yes"]) else "closed"
                            data["lifts"].append({
                                "name": text,
                                "status": status
                            })
        
        # Remove duplicates
        seen_trails = set()
        unique_trails = []
        for trail in data["trails"]:
            if trail["name"] not in seen_trails and trail["name"]:
                seen_trails.add(trail["name"])
                unique_trails.append(trail)
        data["trails"] = unique_trails
        
        seen_lifts = set()
        unique_lifts = []
        for lift in data["lifts"]:
            if lift["name"] not in seen_lifts and lift["name"]:
                seen_lifts.add(lift["name"])
                unique_lifts.append(lift)
        data["lifts"] = unique_lifts
        
        # Add summaries
        data["trails_summary"] = {
            "open": sum(1 for t in data["trails"] if t["status"] == "open"),
            "total": len(data["trails"])
        }
        data["lifts_summary"] = {
            "open": sum(1 for l in data["lifts"] if l["status"] == "open"),
            "total": len(data["lifts"])
        }
        
        return data
        
    finally:
        driver.quit()


def main():
    print("Fetching Caledon Ski Club trail status...")
    status = get_trail_status()
    output_file = os.path.join(os.path.dirname(__file__), "weather-and-status.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")
    return status


if __name__ == "__main__":
    main()
