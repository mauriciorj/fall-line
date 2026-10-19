import json
import os
import sys
import re
import time
import unicodedata
from collections import defaultdict
from urllib.parse import urljoin, urlsplit, urlunsplit

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from convex_client import push_ski_resorts
from dto import to_convex_records

DEFAULT_URL = "https://www.skiresort.info/ski-resorts/"
SKIRESORT_INFO_BASE_URL = "https://www.skiresort.info"


def fetch_html(url):
    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30,
    )
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser")


def parse_skiresort_details(soup):
    text = " ".join(soup.stripped_strings)
    elevation = re.search(
        r"Elevation info\s+([0-9]+(?:[.,][0-9]+)?\s*m\s*[-–]\s*[0-9]+(?:[.,][0-9]+)?\s*m)\s*"
        r"\(Difference\s*([0-9]+(?:[.,][0-9]+)?\s*m)",
        text,
        re.IGNORECASE,
    )
    slope_sections = re.findall(
        r"(?:Runs/slopes|Ski slopes)\s+(.*?)(?=Ski lifts|Worth knowing|Additional runs|Longest run)",
        text,
        re.IGNORECASE,
    )
    slopes = next((section for section in slope_sections if "Easy" in section), None)
    if not elevation or slopes is None:
        raise ValueError("Missing elevation or slope data")

    details = {
        "elevation": re.sub(r"\s*[-–]\s*", " - ", elevation.group(1)),
        "height": elevation.group(2).replace(" ", ""),
    }
    for label, field in (
        ("Easy", "green"),
        ("Intermediate", "blue"),
        ("Difficult", "black"),
    ):
        match = re.search(
            rf"{label}\s+([0-9]+(?:[.,][0-9]+)?\s*km)\s*\(\s*([0-9]+(?:[.,][0-9]+)?)\s*%",
            slopes,
            re.IGNORECASE,
        )
        if not match:
            raise ValueError(f"Missing {label.lower()} slope data")
        details[f"tracks{field.title()}Length"] = match.group(1).replace(" ", "")
        details[f"tracks{field.title()}Proportion"] = match.group(2)
    total = re.search(
        r"Total\s*:\s*([0-9]+(?:[.,][0-9]+)?\s*km)", slopes, re.IGNORECASE
    )
    if not total:
        raise ValueError("Missing total slope data")
    details["tracksTotalLength"] = total.group(1).replace(" ", "")
    return details


def normalize_phone(value):
    digits = re.sub(r"\D", "", value)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return value.strip()


def parse_operator_info(soup):
    panel = soup.find("div", class_="panel panel-default ski-rental")
    if panel is None:
        raise ValueError("Missing lift operator contact panel")

    info = {}
    email_link = panel.find("a", href=lambda href: href and href.startswith("mailto:"))
    phone_link = panel.find("a", href=lambda href: href and href.startswith("tel:"))
    if email_link:
        info["email"] = email_link.get("href", "")[7:]
    if phone_link:
        info["phone"] = normalize_phone(phone_link.get_text(" ", strip=True))

    address = panel.find("address")
    if address:
        info["address"] = " ".join(address.stripped_strings)
    else:
        postal = re.compile(r"[^|]+\b[A-Z]\d[A-Z]\s*\d[A-Z]\d\b[^|]*", re.IGNORECASE)
        match = postal.search(" | ".join(panel.stripped_strings))
        if match:
            info["address"] = " ".join(match.group(0).split())

    if info.get("email") and "@" in info["email"]:
        info["website"] = f"http://{info['email'].split('@', 1)[1].lower()}/"
    return info


def enrich_resort(resort, delay=1.0):
    detail_url = resort.get("url")
    if not detail_url:
        return resort
    time.sleep(delay)
    details = parse_skiresort_details(fetch_html(detail_url))
    operator_url = detail_url.rstrip("/") + "/lift-operator/"
    time.sleep(delay)
    operator = parse_operator_info(fetch_html(operator_url))
    path_parts = [part for part in urlsplit(detail_url).path.split("/") if part]
    resort_id = path_parts[-1] if path_parts else resort.get("id")
    location = resort.get("location", [])
    result = {
        "address": operator.get("address"),
        "continent": location[0] if len(location) > 0 else None,
        "country": location[1] if len(location) > 1 else None,
        "email": operator.get("email"),
        **details,
        "id": resort.get("id"),
        "location": location,
        "name": resort.get("name"),
        "phone": operator.get("phone"),
        "region": location[2] if len(location) > 2 else None,
        "resortId": resort_id,
        "skiresortUrl": detail_url,
        "url": detail_url,
        "website": operator.get("website"),
    }
    return {key: value for key, value in result.items() if value not in (None, "")}


def fetch_ski_resorts(url=DEFAULT_URL, debug=False):
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
        resort_panels = [
            p
            for p in all_panels
            if p.find("a", href=lambda x: x and "/ski-resort/" in x)
        ]
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


def build_page_url(base_url, page):
    if page == 1:
        return base_url
    parts = urlsplit(base_url)
    path = parts.path.rstrip("/")
    return urlunsplit((parts.scheme, parts.netloc, f"{path}/page/{page}/", "", ""))


def fetch_all_pages(base_url=DEFAULT_URL, max_pages=None, delay=1.0):
    """
    Fetch ski resort data from multiple pages.

    Args:
        max_pages: Maximum number of pages to fetch (None for all pages)
        delay: Delay between requests in seconds (be respectful to the server)

    Returns:
        List of all resort data
    """
    all_resorts = []

    # Fetch first page to get total pages
    print(f"Fetching page 1: {base_url}")
    resorts, total_pages = fetch_ski_resorts(base_url)
    all_resorts.extend(resorts)
    print(f"  Found {len(resorts)} resorts (Total pages available: {total_pages})")

    # Determine how many pages to fetch
    pages_to_fetch = total_pages if max_pages is None else min(max_pages, total_pages)

    # Fetch remaining pages
    for page in range(2, pages_to_fetch + 1):
        time.sleep(delay)  # Be respectful to the server
        page_url = build_page_url(base_url, page)
        print(f"Fetching page {page}/{pages_to_fetch}: {page_url}")

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
            resort["url"] = urljoin(SKIRESORT_INFO_BASE_URL, href)
            resort["skiresortUrl"] = resort["url"]

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
                            resort["altitude_difference"] = spans[0].get_text(
                                strip=True
                            )
                            resort["altitude_base"] = spans[1].get_text(strip=True)
                            resort["altitude_top"] = spans[2].get_text(strip=True)

                    # Slopes info
                    elif "icon-uE004-skirun" in icon_class:
                        slope_items = cells[1].find_all("span", class_="slopeinfoitem")
                        if slope_items:
                            resort["slopes_total"] = (
                                slope_items[0].get_text(strip=True)
                                if len(slope_items) > 0
                                else None
                            )
                            resort["slopes_easy"] = (
                                slope_items[1].get_text(strip=True)
                                if len(slope_items) > 1
                                else None
                            )
                            resort["slopes_intermediate"] = (
                                slope_items[2].get_text(strip=True)
                                if len(slope_items) > 2
                                else None
                            )
                            resort["slopes_difficult"] = (
                                slope_items[3].get_text(strip=True)
                                if len(slope_items) > 3
                                else None
                            )

                    # Ski pass price
                    elif "icon-uE001-skipass" in icon_class:
                        resort["ski_pass_price"] = cell_text

                # Lifts info (has different icon structure)
                lift_icon = cells[0].find(
                    "i",
                    class_=lambda x: x and "lift-icon" in " ".join(x) if x else False,
                )
                if lift_icon or (
                    icon and "icon-uE003-lift" in " ".join(icon.get("class", []))
                ):
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
                resort["image_url"] = (
                    "https://www.skiresort.info" + img_url
                    if not img_url.startswith("http")
                    else img_url
                )

    return resort if resort.get("name") else None


def slugify(value):
    normalized = unicodedata.normalize("NFKD", str(value))
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_value.lower()).strip("-")
    if not slug:
        raise ValueError(f"Cannot build a folder name from {value!r}")
    return slug


def resort_location(resort):
    location = resort.get("location", [])
    country = resort.get("country") or (
        location[1] if isinstance(location, list) and len(location) > 1 else None
    )
    region = resort.get("region") or (
        location[2] if isinstance(location, list) and len(location) > 2 else None
    )
    if not country or not region:
        raise ValueError(
            f"Missing country or region for resort {resort.get('resortId') or resort.get('name')}"
        )
    return country, region


def save_to_json(data, output_root=None):
    """Save one JSON file per country and region."""

    output_root = (
        os.path.abspath(output_root)
        if output_root
        else os.path.dirname(os.path.abspath(__file__))
    )
    grouped = defaultdict(list)
    for resort in data:
        country, region = resort_location(resort)
        grouped[(slugify(country), slugify(region))].append(resort)

    filepaths = []
    for (country, region), resorts in sorted(grouped.items()):
        directory = os.path.join(output_root, country, region)
        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, "ski-resorts-list.json")
        with open(filepath, "w", encoding="utf-8") as output:
            json.dump(resorts, output, indent=2, ensure_ascii=False)
        filepaths.append(filepath)
        print(f"Data saved to {filepath}")
    return filepaths


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Crawl ski resort data from skiresort.info"
    )
    parser.add_argument(
        "url",
        nargs="?",
        default=DEFAULT_URL,
        help=f"Ski resort listing URL (default: {DEFAULT_URL})",
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=1,
        help="Number of pages to fetch (default: 1, use 0 for all pages)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between page requests in seconds (default: 1.0)",
    )
    parser.add_argument(
        "--details-delay",
        type=float,
        default=1.0,
        help="Delay between resort detail requests (default: 1.0)",
    )
    parser.add_argument(
        "--output-root",
        type=str,
        default=None,
        help="Root folder for country/region output files (default: this script folder)",
    )
    args = parser.parse_args()

    print("Fetching ski resort data from skiresort.info...")

    try:
        if args.pages == 1:
            # Single page mode
            resorts, total_pages = fetch_ski_resorts(args.url)
            print(
                f"Found {len(resorts)} ski resorts on page 1 "
                f"(Total pages available: {total_pages})"
            )
        else:
            # Multi-page mode
            max_pages = None if args.pages == 0 else args.pages
            resorts = fetch_all_pages(
                base_url=args.url,
                max_pages=max_pages,
                delay=args.delay,
            )

        enriched_resorts = []
        for index, resort in enumerate(resorts, start=1):
            print(
                f"Enriching resort {index}/{len(resorts)}: {resort.get('name', 'unknown')}"
            )
            try:
                enriched_resorts.append(enrich_resort(resort, delay=args.details_delay))
            except Exception as error:
                print(f"  Error enriching {resort.get('name', 'unknown')}: {error}")
        resorts = enriched_resorts

        if resorts:
            print(f"\nTotal resorts collected: {len(resorts)}")
            save_to_json(resorts, args.output_root)
            push_result = push_ski_resorts(
                to_convex_records(resorts),
                function_path="skiresortinfo:saveMany",
            )
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
