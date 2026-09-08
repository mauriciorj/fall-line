import json
import os
import sys
import time

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from convex_client import push_ski_resorts
from dto import to_convex_records


def fetch_ski_resorts(url="https://www.skiresort.info/ski-resorts/", debug=False):
    """Fetch ski resort data from a single page of skiresort.info"""
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, "html.parser")
    
    if debug:
        # Save full HTML for debugging
        with open("debug_full.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())
        print("Debug: Saved full HTML to debug_full.html")
    
    resorts = []
    
    # Find resort list container - look for the resort-list-item divs
    resort_panels = soup.find_all("div", class_="resort-list-item")
    
    if debug:
        print(f"Debug: Found {len(resort_panels)} resort-list-item divs")
    
    # If not found, try finding by the panel structure within resort list
    if not resort_panels:
        # Try finding panels that contain resort links
        all_panels = soup.find_all("div", class_="panel")
        resort_panels = [p for p in all_panels if p.find("a", href=lambda x: x and "/ski-resort/" in x)]
        if debug:
            print(f"Debug: Found {len(resort_panels)} panels with ski-resort links")
    
    if debug and resort_panels:
        with open("debug_panel.html", "w", encoding="utf-8") as f:
            f.write(str(resort_panels[0]))
        print("Debug: Saved first resort panel to debug_panel.html")
    
    for panel in resort_panels:
        resort_data = extract_resort_info(panel)
        if resort_data:
            resorts.append(resort_data)
    
    # Find total pages from pagination
    total_pages = 1
    pagination = soup.find("ul", class_="pagination")
    if pagination:
        page_links = pagination.find_all("a")
        for link in page_links:
            href = link.get("href", "")
            # Extract page number from URL like "/ski-resorts/page/32/"
            if "/page/" in href:
                try:
                    page_num = int(href.rstrip("/").split("/")[-1])
                    total_pages = max(total_pages, page_num)
                except ValueError:
                    continue
    
    return resorts, total_pages


def fetch_all_pages(max_pages=None, delay=1.0):
    """
    Fetch ski resort data from multiple pages.
    
    Args:
        max_pages: Maximum number of pages to fetch (None for all pages)
        delay: Delay between requests in seconds (be respectful to the server)
    
    Returns:
        List of all resort data
    """
    base_url = "https://www.skiresort.info/ski-resorts/"
    all_resorts = []
    
    # Fetch first page to get total pages
    print("Fetching page 1...")
    resorts, total_pages = fetch_ski_resorts(base_url)
    all_resorts.extend(resorts)
    print(f"  Found {len(resorts)} resorts (Total pages available: {total_pages})")
    
    # Determine how many pages to fetch
    pages_to_fetch = total_pages if max_pages is None else min(max_pages, total_pages)
    
    # Fetch remaining pages
    for page in range(2, pages_to_fetch + 1):
        time.sleep(delay)  # Be respectful to the server
        page_url = f"{base_url}page/{page}/"
        print(f"Fetching page {page}/{pages_to_fetch}...")
        
        try:
            resorts, _ = fetch_ski_resorts(page_url)
            all_resorts.extend(resorts)
            print(f"  Found {len(resorts)} resorts (Total so far: {len(all_resorts)})")
        except Exception as e:
            print(f"  Error fetching page {page}: {e}")
            continue
    
    return all_resorts


def extract_resort_info(panel):
    """Extract information from a single resort panel/card"""
    
    resort = {}
    
    # Extract resort ID from panel
    resort_id = panel.get("id", "")
    if resort_id:
        resort["id"] = resort_id
    
    # Extract resort name and URL
    name_elem = panel.find("a", class_="h3")
    if name_elem:
        resort["name"] = name_elem.get_text(strip=True)
        href = name_elem.get("href", "")
        if href:
            resort["url"] = href if href.startswith("http") else "https://www.skiresort.info" + href
    
    # Extract location breadcrumb
    breadcrumb_elem = panel.find("div", class_="sub-breadcrumb")
    if breadcrumb_elem:
        location_links = breadcrumb_elem.find_all("a")
        resort["location"] = [link.get_text(strip=True) for link in location_links]
    
    # Extract rating from star element
    star_elem = panel.find("div", class_="js-star-ranking")
    if star_elem:
        rating = star_elem.get("data-rank")
        if rating:
            resort["rating"] = float(rating)
    
    # Extract info from table rows
    info_table = panel.find("table", class_="info-table")
    if info_table:
        rows = info_table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 2:
                # Check for icon type to determine data category
                icon = cells[0].find("i")
                cell_text = cells[1].get_text(strip=True)
                
                if icon:
                    icon_class = " ".join(icon.get("class", []))
                    
                    # Height/Altitude info
                    if "icon-uE002-height" in icon_class:
                        spans = cells[1].find_all("span")
                        if len(spans) >= 3:
                            resort["altitude_difference"] = spans[0].get_text(strip=True)
                            resort["altitude_base"] = spans[1].get_text(strip=True)
                            resort["altitude_top"] = spans[2].get_text(strip=True)
                    
                    # Slopes info
                    elif "icon-uE004-skirun" in icon_class:
                        slope_items = cells[1].find_all("span", class_="slopeinfoitem")
                        if slope_items:
                            resort["slopes_total"] = slope_items[0].get_text(strip=True) if len(slope_items) > 0 else None
                            resort["slopes_easy"] = slope_items[1].get_text(strip=True) if len(slope_items) > 1 else None
                            resort["slopes_intermediate"] = slope_items[2].get_text(strip=True) if len(slope_items) > 2 else None
                            resort["slopes_difficult"] = slope_items[3].get_text(strip=True) if len(slope_items) > 3 else None
                    
                    # Ski pass price
                    elif "icon-uE001-skipass" in icon_class:
                        resort["ski_pass_price"] = cell_text
                
                # Lifts info (has different icon structure)
                lift_icon = cells[0].find("i", class_=lambda x: x and "lift-icon" in " ".join(x) if x else False)
                if lift_icon or (icon and "icon-uE003-lift" in " ".join(icon.get("class", []))):
                    li_elem = cells[1].find("li")
                    if li_elem:
                        resort["lifts"] = li_elem.get_text(strip=True)
    
    # Extract main image URL (use data-src for lazy-loaded images)
    img_wrap = panel.find("div", class_="resort-list-default-img")
    if img_wrap:
        img_elem = img_wrap.find("img")
        if img_elem:
            img_url = img_elem.get("data-src") or img_elem.get("src")
            if img_url and not img_url.endswith("1x1-0000ff7f.png"):
                resort["image_url"] = "https://www.skiresort.info" + img_url if not img_url.startswith("http") else img_url
    
    return resort if resort.get("name") else None


def save_to_json(data, filename="ski-resorts-list.json"):
    """Save the scraped data to a JSON file"""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Data saved to {filepath}")
    return filepath


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Crawl ski resort data from skiresort.info")
    parser.add_argument("--pages", type=int, default=1, 
                        help="Number of pages to fetch (default: 1, use 0 for all pages)")
    parser.add_argument("--delay", type=float, default=1.0,
                        help="Delay between page requests in seconds (default: 1.0)")
    parser.add_argument("--output", type=str, default="ski-resorts-list.json",
                        help="Output JSON filename (default: ski-resorts-list.json)")
    args = parser.parse_args()
    
    print("Fetching ski resort data from skiresort.info...")
    
    try:
        if args.pages == 1:
            # Single page mode
            resorts, total_pages = fetch_ski_resorts()
            print(f"Found {len(resorts)} ski resorts on page 1 (Total pages available: {total_pages})")
        else:
            # Multi-page mode
            max_pages = None if args.pages == 0 else args.pages
            resorts = fetch_all_pages(max_pages=max_pages, delay=args.delay)
        
        if resorts:
            print(f"\nTotal resorts collected: {len(resorts)}")
            filepath = save_to_json(resorts, args.output)
            push_result = push_ski_resorts(to_convex_records(resorts))
            if push_result is not None:
                print(f"Pushed {len(resorts)} records to Convex")
            
            # Print sample of first resort
            print("\nSample resort data:")
            print(json.dumps(resorts[0], indent=2, ensure_ascii=True))
        else:
            print("No resorts found. The page structure may have changed.")
            print("Please check the HTML structure and update the selectors.")
            
    except requests.RequestException as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
