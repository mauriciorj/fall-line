import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

URL = "https://www.discoverchicopee.com/contact#hours"


def get_driver():
    """Create and return a configured Chrome WebDriver."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    service = Service()
    return webdriver.Chrome(service=service, options=options)


def extract_hours_section(soup):
    """Extract hours of operation from the page."""
    result = {}
    
    hours_heading = soup.find(["h2", "h3"], string=lambda s: s and "hours of operation" in s.lower() if s else False)
    
    if not hours_heading:
        headings = soup.find_all(["h2", "h3"])
        for h in headings:
            if h.get_text(strip=True).lower() == "hours of operation":
                hours_heading = h
                break
    
    if not hours_heading:
        return result
    
    parent = hours_heading.find_parent(["section", "div"])
    if not parent:
        parent = hours_heading.parent
    
    h3_sections = parent.find_all("h3")
    
    for h3 in h3_sections:
        section_name = h3.get_text(strip=True)
        if not section_name or section_name.lower() == "hours of operation":
            continue
        
        section_hours = {}
        
        next_elem = h3.find_next_sibling()
        while next_elem and next_elem.name != "h3":
            if next_elem.name in ["div", "p", "ul", "table"]:
                text = next_elem.get_text(separator="\n", strip=True)
                lines = [line.strip() for line in text.split("\n") if line.strip()]
                
                i = 0
                while i < len(lines):
                    line = lines[i]
                    if any(day in line for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Daily", "Weekday", "Weekend"]):
                        day_key = line.rstrip(":")
                        if i + 1 < len(lines) and not any(d in lines[i + 1] for d in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Daily", "Weekday", "Weekend"]):
                            section_hours[day_key] = lines[i + 1]
                            i += 2
                        else:
                            parts = line.split(":", 1)
                            if len(parts) == 2 and parts[1].strip():
                                section_hours[parts[0].strip()] = parts[1].strip()
                            i += 1
                    else:
                        i += 1
            next_elem = next_elem.find_next_sibling()
        
        if section_hours:
            result[section_name] = section_hours
    
    if not result:
        result = extract_hours_fallback(parent)
    
    return result


def extract_hours_fallback(container):
    """Fallback extraction by parsing all text content."""
    result = {}
    
    text = container.get_text(separator="\n", strip=True)
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    current_section = None
    i = 0
    
    section_keywords = ["guest services", "lift hours", "food", "beverage", "rental", "lesson", "ticket"]
    day_keywords = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Daily", "Weekday", "Weekend"]
    
    while i < len(lines):
        line = lines[i]
        
        if any(keyword in line.lower() for keyword in section_keywords) and len(line) < 50:
            current_section = line
            if current_section not in result:
                result[current_section] = {}
            i += 1
            continue
        
        if any(day in line for day in day_keywords):
            if current_section:
                if ":" in line:
                    parts = line.split(":", 1)
                    day_key = parts[0].strip()
                    time_val = parts[1].strip() if len(parts) > 1 else ""
                    if time_val:
                        result[current_section][day_key] = time_val
                    elif i + 1 < len(lines):
                        result[current_section][day_key] = lines[i + 1]
                        i += 1
                else:
                    day_key = line
                    if i + 1 < len(lines) and not any(d in lines[i + 1] for d in day_keywords):
                        result[current_section][day_key] = lines[i + 1]
                        i += 1
        i += 1
    
    result = {k: v for k, v in result.items() if v}
    return result


def get_hours():
    """Fetch and parse hours of operation from Chicopee."""
    print(f"Fetching {URL}...")
    driver = get_driver()
    result = {}

    try:
        driver.get(URL)
        time.sleep(5)
        
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Hours of Operation') or contains(text(), 'hours of operation')]"))
            )
        except:
            pass

        soup = BeautifulSoup(driver.page_source, "html.parser")
        result = extract_hours_section(soup)
        
        if not result:
            all_divs = soup.find_all("div")
            for div in all_divs:
                div_text = div.get_text(strip=True).lower()
                if "hours of operation" in div_text and len(div_text) < 2000:
                    result = extract_hours_fallback(div)
                    if result:
                        break

    finally:
        driver.quit()

    return result


def main():
    hours = get_hours()
    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(hours, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")
    return hours


if __name__ == "__main__":
    main()
