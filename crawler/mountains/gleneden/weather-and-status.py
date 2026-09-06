import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


def get_trail_status():
    """
    Crawl Glen Eden's slope conditions page to extract trail and lift status.
    Uses Selenium because the page may be rendered with JavaScript.
    """
    url = "https://gleneden.on.ca/at-glen-eden/slope-conditions/"
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(url)
        time.sleep(5)
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        data = {
            "conditions": {},
            "lifts": [],
            "trails": []
        }
        
        # Extract general slope conditions
        # Look for condition info like base depth, snow conditions
        condition_texts = soup.find_all(string=lambda s: s and any(
            keyword in s.lower() for keyword in ["base depth", "groomed", "new snow", "snowmaking"]
        ) if s else False)
        
        for text in condition_texts:
            text_clean = text.strip()
            if "base depth" in text_clean.lower():
                data["conditions"]["base_depth"] = text_clean
            elif "groomed" in text_clean.lower():
                data["conditions"]["snow_condition"] = text_clean
            elif "new snow" in text_clean.lower():
                data["conditions"]["new_snow"] = text_clean
            elif "snowmaking" in text_clean.lower():
                data["conditions"]["snowmaking"] = text_clean
        
        # Find all tables on the page for lifts and trails
        tables = soup.find_all("table")
        
        for table in tables:
            rows = table.find_all("tr")
            if not rows:
                continue
            
            # Check header to determine table type
            header_row = rows[0]
            header_text = header_row.get_text(strip=True).lower()
            
            for row in rows[1:]:  # Skip header
                cells = row.find_all("td")
                if not cells:
                    continue
                
                # Extract status from cell content or icons
                row_data = []
                for cell in cells:
                    # Check for status icons (open/closed)
                    img = cell.find("img")
                    if img:
                        alt = img.get("alt", "").lower()
                        src = img.get("src", "").lower()
                        if "open" in alt or "open" in src or "green" in src:
                            row_data.append("Open")
                        elif "closed" in alt or "closed" in src or "red" in src:
                            row_data.append("Closed")
                        else:
                            row_data.append(cell.get_text(strip=True))
                    else:
                        row_data.append(cell.get_text(strip=True))
                
                if len(row_data) >= 2:
                    item = {
                        "name": row_data[0],
                        "status": row_data[1] if len(row_data) > 1 else ""
                    }
                    if len(row_data) > 2:
                        item["extra"] = row_data[2:]
                    
                    # Categorize as lift or trail based on name patterns
                    name_lower = row_data[0].lower()
                    if any(keyword in name_lower for keyword in ["lift", "carpet", "magic", "chair", "t-bar"]):
                        data["lifts"].append(item)
                    else:
                        data["trails"].append(item)
        
        # Alternative: Look for divs/sections with trail/lift info
        if not data["trails"] and not data["lifts"]:
            # Try finding sections by class or heading
            sections = soup.find_all(["div", "section"])
            
            for section in sections:
                heading = section.find(["h2", "h3", "h4"])
                if heading:
                    heading_text = heading.get_text(strip=True).lower()
                    
                    # Find list items or paragraphs with status
                    items = section.find_all(["li", "p", "div"], recursive=False)
                    for item in items:
                        text = item.get_text(strip=True)
                        if text and len(text) > 2:
                            # Check for status indicators
                            status = "Unknown"
                            if "open" in text.lower():
                                status = "Open"
                            elif "closed" in text.lower():
                                status = "Closed"
                            
                            entry = {"name": text, "status": status}
                            
                            if "lift" in heading_text:
                                data["lifts"].append(entry)
                            elif "trail" in heading_text or "run" in heading_text or "slope" in heading_text:
                                data["trails"].append(entry)
        
        # Calculate summaries
        total_lifts = len(data["lifts"])
        open_lifts = sum(1 for l in data["lifts"] if "open" in l.get("status", "").lower())
        data["lifts_summary"] = {"open": open_lifts, "total": total_lifts}
        
        total_trails = len(data["trails"])
        open_trails = sum(1 for t in data["trails"] if "open" in t.get("status", "").lower())
        data["trails_summary"] = {"open": open_trails, "total": total_trails}
        
        return data
        
    finally:
        driver.quit()


def main():
    print("Fetching Glen Eden trail status...")
    status = get_trail_status()
    output_file = os.path.join(os.path.dirname(__file__), "weather-and-status.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")
    return status


if __name__ == "__main__":
    main()
