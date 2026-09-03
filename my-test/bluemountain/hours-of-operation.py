import requests
from bs4 import BeautifulSoup
import json
import re
import os

URL = "https://www.bluemountain.ca/mountain/hours"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def clean_text(text):
    """Clean and normalize text by removing extra whitespace."""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()


def extract_hours_from_card(card):
    """Extract hours information from a single card/item."""
    hours_data = {}
    
    # Find all schedule rows within the card
    rows = card.find_all("div", class_=re.compile(r"schedule|hours|row", re.I))
    
    # Look for day/time patterns in the card text
    text_content = card.get_text(separator="\n", strip=True)
    lines = [line.strip() for line in text_content.split("\n") if line.strip()]
    
    current_period = None
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check for date range headers (e.g., "As Of Dec. 11", "Jan. 5 - Mar. 12")
        if re.match(r'^(As Of|Dec\.|Jan\.|Feb\.|Mar\.|Apr\.|May|Jun\.|Jul\.|Aug\.|Sep\.|Oct\.|Nov\.)', line, re.I):
            current_period = clean_text(line)
            if current_period not in hours_data:
                hours_data[current_period] = {}
            i += 1
            continue
        
        # Check for day patterns (e.g., "DAILY", "MON. - FRI.", "MONDAY")
        day_pattern = r'^(DAILY|MON\.?|TUES?\.?|WED\.?|THURS?\.?|FRI\.?|SAT\.?|SUN\.?|MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY)'
        day_match = re.match(day_pattern, line, re.I)
        
        if day_match:
            day_key = clean_text(line)
            # Next line should be the time
            if i + 1 < len(lines):
                time_line = lines[i + 1]
                # Check if it looks like a time (contains AM/PM or numbers with colon)
                if re.search(r'\d+[:\d]*\s*(AM|PM)|CLOSED', time_line, re.I):
                    if current_period:
                        hours_data[current_period][day_key] = clean_text(time_line)
                    else:
                        hours_data[day_key] = clean_text(time_line)
                    i += 2
                    continue
        i += 1
    
    return hours_data


def extract_section_hours(section):
    """Extract all hours from a section (Attractions, Dining, etc.)."""
    results = {}
    
    # Find all cards/items in this section
    cards = section.find_all("div", class_=re.compile(r"card|item|accordion", re.I))
    
    if not cards:
        # Try finding by looking for heading patterns
        cards = section.find_all("div", recursive=False)
    
    for card in cards:
        # Try to find the name/title of this item
        title_elem = card.find(["h2", "h3", "h4", "h5", "h6", "strong"])
        if not title_elem:
            title_elem = card.find("a")
        
        if title_elem:
            title = clean_text(title_elem.get_text())
            if title and len(title) > 2:
                hours = extract_hours_from_card(card)
                if hours:
                    results[title] = hours
    
    return results


def parse_hours_page(soup):
    """Parse the entire hours page and extract all hours of operation."""
    all_hours = {}
    
    # Find main content area
    main_content = soup.find("main") or soup.find("div", class_=re.compile(r"content|main", re.I)) or soup
    
    # Look for section headers
    sections = main_content.find_all("section") or main_content.find_all("div", class_=re.compile(r"section|accordion", re.I))
    
    if sections:
        for section in sections:
            section_title_elem = section.find(["h1", "h2", "h3"])
            if section_title_elem:
                section_title = clean_text(section_title_elem.get_text())
                if section_title:
                    section_hours = extract_section_hours(section)
                    if section_hours:
                        all_hours[section_title] = section_hours
    
    # If no structured sections found, try parsing the whole page
    if not all_hours:
        all_hours = extract_hours_from_page_text(soup)
    
    return all_hours


def extract_hours_from_page_text(soup):
    """Fallback: Extract hours by parsing the page text directly."""
    results = {}
    
    # Get all text content
    text = soup.get_text(separator="\n", strip=True)
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    current_section = None
    current_item = None
    current_period = None
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Skip navigation and boilerplate
        if len(line) < 3 or line in ["rich-text, responsive-table", "map-box-component"]:
            i += 1
            continue
        
        # Check for major section headers
        section_match = re.match(r'^(ATTRACTIONS|GUEST SERVICES|LODGING|DINING|SHOPPING|RENTALS)', line, re.I)
        if section_match:
            current_section = line.title()
            if current_section not in results:
                results[current_section] = {}
            current_item = None
            current_period = None
            i += 1
            continue
        
        # Check for date range/period headers
        period_match = re.match(r'^(As Of .+|[A-Z][a-z]{2,3}\.\s*\d+\s*-\s*.+)$', line)
        if period_match:
            current_period = clean_text(line)
            i += 1
            continue
        
        # Check for day patterns
        day_pattern = r'^(DAILY|MON\.?|TUES?\.?|WED\.?|THURS?\.?|FRI\.?|SAT\.?|SUN\.?|MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY)(\s*[-&]\s*(MON\.?|TUES?\.?|WED\.?|THURS?\.?|FRI\.?|SAT\.?|SUN\.?|MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY))?\.?$'
        day_match = re.match(day_pattern, line, re.I)
        
        if day_match:
            day_key = clean_text(line)
            # Next line should be the time
            if i + 1 < len(lines):
                time_line = lines[i + 1]
                if re.search(r'\d+[:\d]*\s*(AM|PM)|CLOSED', time_line, re.I):
                    if current_section and current_item:
                        if current_item not in results[current_section]:
                            results[current_section][current_item] = {}
                        
                        if current_period:
                            if current_period not in results[current_section][current_item]:
                                results[current_section][current_item][current_period] = {}
                            results[current_section][current_item][current_period][day_key] = clean_text(time_line)
                        else:
                            results[current_section][current_item][day_key] = clean_text(time_line)
                    i += 2
                    continue
        
        # Check if this might be an item name (not a day, not a time, not too long)
        if (current_section and 
            not day_match and 
            not re.search(r'\d+[:\d]*\s*(AM|PM)', line, re.I) and
            len(line) > 3 and len(line) < 60 and
            not line.startswith("As Of") and
            not re.match(r'^[A-Z][a-z]{2,3}\.\s*\d+', line)):
            # This could be an item name
            potential_item = clean_text(line)
            # Check if next lines contain schedule info
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                if (re.match(day_pattern, next_line, re.I) or 
                    re.match(r'^(As Of|[A-Z][a-z]{2,3}\.\s*\d+)', next_line)):
                    current_item = potential_item
                    current_period = None
        
        i += 1
    
    return results


def get_hours():
    """Fetch and parse hours of operation from Blue Mountain."""
    print(f"Fetching {URL}...")
    response = requests.get(URL, headers=HEADERS)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, "html.parser")
    return parse_hours_page(soup)


def main():
    hours = get_hours()
    output_file = os.path.join(os.path.dirname(__file__), "hours-of-operation.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(hours, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
