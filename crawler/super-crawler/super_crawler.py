import argparse
import heapq
import itertools
import json
import os
import re
import sys
import time
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from extractors import (
    ACTIVITY_PATTERNS,
    CA_POSTAL_RE,
    analyze_page,
    document_categories,
    link_priority,
    province_from_postal,
    score_categories,
)
from fetcher import (
    Fetcher,
    is_document,
    lang_prefix,
    normalize_url,
    origin,
    site_host,
    skip_reason,
    url_key,
)

TARGET_CATEGORIES = ("contact", "hours", "rates", "rentals", "trails", "lessons")
GENERATOR_CATEGORIES = {
    "hours": "hours-of-operation.py",
    "rates": "lift-rates.py",
    "rentals": "rentals.py",
    "trails": "tracks-and-lifts-weather-status.py",
}
MIN_CATEGORY_SCORE = 5
TOP_PAGES = 5
NORTH_AMERICA = {"Canada", "United States"}


def slugify(value):
    ascii_value = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore")
    return re.sub(r"[^a-z0-9]+", "-", ascii_value.decode("ascii").lower()).strip("-")


def crawl(start_url, fetcher, max_pages, max_depth, render):
    start = normalize_url(start_url)
    host, start_lang = site_host(start), lang_prefix(start)
    queue, order = [], itertools.count()
    queued, fetched = set(), set()
    anchors = defaultdict(set)
    documents = {}
    skipped = Counter()

    def enqueue(url, depth, text=""):
        url = normalize_url(url)
        if is_document(url):
            documents.setdefault(url, set()).add(text)
            return
        reason = skip_reason(url, host, start_lang)
        if reason:
            skipped[reason] += 1
            return
        key = url_key(url)
        if text:
            anchors[key].add(text)
        if key not in queued:
            queued.add(key)
            priority = 1000 if depth == 0 else link_priority(url, text, depth)
            heapq.heappush(queue, (-priority, next(order), url, depth))

    enqueue(start, 0)
    for url in fetcher.sitemap_urls(start):
        enqueue(url, 1)

    pages, errors, attempts = [], [], 0
    while queue and len(pages) < max_pages and attempts < max_pages * 3:
        _, _, url, depth = heapq.heappop(queue)
        attempts += 1
        if not fetcher.allowed(url):
            skipped["robots"] += 1
            continue
        try:
            response = fetcher.get(url)
        except requests.RequestException as error:
            errors.append({"url": url, "error": str(error)})
            continue

        final = normalize_url(response.url)
        if url_key(final) in fetched or site_host(final) != host:
            skipped["redirect"] += 1
            continue
        fetched.update({url_key(url), url_key(final)})
        content_type = response.headers.get("Content-Type", "").lower()
        if "pdf" in content_type:
            documents.setdefault(final, set())
            continue
        if "html" not in content_type:
            skipped["non-html"] += 1
            continue

        page = analyze_page(final, BeautifulSoup(response.content, "html.parser"), response.text)
        page["rendered"] = False
        if render and page["needsJs"]:
            try:
                html = fetcher.render_html(final)
                page = analyze_page(final, BeautifulSoup(html, "html.parser"), html)
                page.update(needsJs=True, rendered=True)
            except Exception as error:
                errors.append({"url": final, "error": f"render failed: {error}"})
        page["depth"] = depth
        print(f"[{len(pages) + 1}/{max_pages}] {final}")
        if depth < max_depth:
            for link, text in page["links"]:
                enqueue(link, depth + 1, text)
        page["linkCount"] = len(page.pop("links"))
        pages.append(page)

    return {
        "pages": pages,
        "anchors": anchors,
        "documents": documents,
        "skipped": dict(skipped),
        "errors": errors,
        "queueRemaining": len(queue),
    }


def rank(entries, limit=10):
    stats = {}
    for value, weight, url in entries:
        item = stats.setdefault(value, {"value": value, "score": 0, "sources": []})
        item["score"] += weight
        if url not in item["sources"] and len(item["sources"]) < 5:
            item["sources"].append(url)
    return sorted(stats.values(), key=lambda item: -item["score"])[:limit]


def aggregate_facts(pages, host):
    def email_weight(email):
        domain = email.rsplit("@", 1)[-1].lower()
        return 2 if domain.endswith(host) or host.endswith(domain) else 1

    coordinates = next((c for page in pages for c in page["coordinates"]), None)
    return {
        "names": rank(
            [(page["siteName"], 3, page["url"]) for page in pages if page["siteName"]]
            + [(name, 2, page["url"]) for page in pages for name in page["names"]]
        ),
        "emails": rank(
            [(e.lower(), email_weight(e), page["url"]) for page in pages for e in page["emails"]]
        ),
        "phones": rank(
            [
                (phone, 3 if source == "tel" else 1, page["url"])
                for page in pages
                for source, phone in page["phones"]
            ]
        ),
        "addresses": rank(
            [
                (address, 50 if source == "json-ld" else 1, page["url"])
                for page in pages
                for source, address in page["addresses"]
            ]
        ),
        "coordinates": coordinates,
        "openingHours": [
            {"url": page["url"], "value": value}
            for page in pages
            for value in page["openingHours"]
        ][:10],
    }


def aggregate_activities(pages, complete):
    result = {}
    for name in ACTIVITY_PATTERNS:
        evidence = [
            {"url": page["url"], **page["activities"][name]}
            for page in pages
            if name in page["activities"]
        ]
        positive = [item for item in evidence if not item["negated"]]
        if any(item["strong"] for item in positive):
            value, confidence = True, "high"
        elif len(positive) >= 2:
            value, confidence = True, "medium"
        elif evidence:
            value, confidence = None, "low"
        elif complete:
            value, confidence = False, "medium"
        else:
            value, confidence = None, "unknown"
        result[name] = {
            "value": value,
            "confidence": confidence,
            "pagesMentioning": len(evidence),
            "evidence": sorted(evidence, key=lambda item: (-item["strong"], -item["mentions"]))[:5],
        }
    return result


def page_summary(page, category):
    summary = {
        "url": page["url"],
        "title": page["title"],
        "score": page["scores"][category],
        "needsJs": page["needsJs"],
        "rendered": page["rendered"],
        "iframes": page["iframes"],
        "apiEndpoints": page["apiEndpoints"],
    }
    if category in ("rates", "rentals", "lessons"):
        summary.update(priceCount=page["priceCount"], priceSnippets=page["priceSnippets"])
    if category == "hours":
        summary.update(hoursSnippets=page["hoursSnippets"], openingHours=page["openingHours"])
    if category == "trails":
        summary.update(
            trailElements=page["trailElements"], difficultyMarkers=page["difficultyMarkers"]
        )
    if category != "contact":
        summary["tables"] = page["tables"]
    return summary


def build_page_map(pages, anchors):
    for page in pages:
        page["scores"] = score_categories(page, " ".join(anchors.get(url_key(page["url"]), ())))
    return {
        category: [
            page_summary(page, category)
            for page in sorted(pages, key=lambda p: -p["scores"].get(category, 0))
            if page["scores"].get(category, 0) >= MIN_CATEGORY_SCORE
        ][:TOP_PAGES]
        for category in TARGET_CATEGORIES
    }


def build_static_infos(args, start_url, facts, activities, page_map, host):
    def best(key):
        return facts[key][0]["value"] if facts[key] else None

    name = args.name or best("names")
    address = best("addresses")
    postal = CA_POSTAL_RE.search(address or "")
    country = args.country or ("Canada" if postal else None)
    region = args.region or (province_from_postal(postal.group(1)) if postal else None)
    continent = args.continent or ("North America" if country in NORTH_AMERICA else None)
    resort_id = args.resort_id or slugify(name) or slugify(host.split(".")[0])
    draft = {
        "address": address,
        "continent": continent,
        "coordinates": facts["coordinates"],
        "country": country,
        "email": best("emails"),
        "name": name,
        "phone": best("phones"),
        "published": False,
        "region": region,
        "resortId": resort_id,
        "ticketUrl": page_map["rates"][0]["url"] if page_map["rates"] else None,
        "website": f"{origin(start_url)}/",
        **{flag: item["value"] for flag, item in activities.items()},
    }
    return {key: value for key, value in draft.items() if value is not None}


def review_notes(static_infos, facts, activities, page_map, crawl_result, complete):
    notes = []
    if not complete:
        notes.append(
            f"Crawl stopped with {crawl_result['queueRemaining']} URLs left in the queue; "
            "activity flags without evidence were not set to false. Raise --max-pages to crawl more."
        )
    for field in ("address", "email", "phone", "name", "coordinates", "country", "region"):
        if field not in static_infos:
            notes.append(f"static_infos: '{field}' not found; fill it from a verified source.")
    for flag, item in activities.items():
        if item["confidence"] in ("medium", "low", "unknown") and item["value"] is not False:
            notes.append(f"{flag}: {item['confidence']} confidence ({item['pagesMentioning']} pages); check evidence.")
    for category, generator in GENERATOR_CATEGORIES.items():
        pages = page_map[category]
        if not pages:
            hint = " JSON-LD openingHours exists in facts." if category == "hours" and facts["openingHours"] else ""
            notes.append(f"{category}: no candidate page found for {generator}; check documents or ask for the URL.{hint}")
        elif pages[0]["needsJs"]:
            action = "" if pages[0]["rendered"] else " Rerun with --render to inspect it."
            notes.append(
                f"{category}: top page {pages[0]['url']} is JavaScript-rendered.{action} "
                "The generator must use Selenium."
            )
        elif pages[0]["iframes"] or pages[0]["apiEndpoints"]:
            notes.append(
                f"{category}: top page {pages[0]['url']} embeds iframes/API endpoints; "
                "the data may come from a third-party source."
            )
    return notes


def build_discovery(args, crawl_result, start_url, host):
    pages = crawl_result["pages"]
    complete = crawl_result["queueRemaining"] == 0
    facts = aggregate_facts(pages, host)
    activities = aggregate_activities(pages, complete)
    page_map = build_page_map(pages, crawl_result["anchors"])
    static_infos = build_static_infos(args, start_url, facts, activities, page_map, host)
    iframes = defaultdict(set)
    for page in pages:
        for frame in page["iframes"]:
            iframes[site_host(frame)].add(frame)
    discovery = {
        "resortId": static_infos["resortId"],
        "startUrl": start_url,
        "crawledAt": int(time.time() * 1000),
        "settings": {
            "maxPages": args.max_pages,
            "maxDepth": args.max_depth,
            "delay": args.delay,
            "render": args.render,
        },
        "stats": {
            "pagesFetched": len(pages),
            "complete": complete,
            "queueRemaining": crawl_result["queueRemaining"],
            "skipped": crawl_result["skipped"],
            "errors": crawl_result["errors"][:50],
        },
        "facts": facts,
        "activities": activities,
        "pageMap": page_map,
        "documents": [
            {
                "url": url,
                "linkText": sorted(t for t in texts if t),
                "categories": document_categories(url, " ".join(texts)),
            }
            for url, texts in sorted(crawl_result["documents"].items())
        ],
        "thirdParty": {
            "iframes": {domain: sorted(urls)[:5] for domain, urls in sorted(iframes.items())},
            "apiEndpoints": sorted({e for page in pages for e in page["apiEndpoints"]})[:50],
        },
        "needsReview": review_notes(static_infos, facts, activities, page_map, crawl_result, complete),
        "pages": [
            {
                "url": page["url"],
                "title": page["title"],
                "depth": page["depth"],
                "textLength": page["textLength"],
                "needsJs": page["needsJs"],
                "rendered": page["rendered"],
                "scores": page["scores"],
            }
            for page in pages
        ],
    }
    return discovery, static_infos


def msys_root():
    exe_path = os.environ.get("EXEPATH") if os.environ.get("MSYSTEM") else None
    if not exe_path:
        return None
    root = Path(exe_path)
    return root.parent if root.name.lower() == "bin" else root


def resolve_output_dir(value):
    path = Path(value)
    root = msys_root()
    if root and path.is_absolute() and path.is_relative_to(root):
        path = path.relative_to(root)
    elif os.name == "nt" and not path.drive:
        path = Path(str(path).lstrip("/\\"))
    return path.resolve() if path.is_absolute() else (ROOT / path).resolve()


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as output:
        json.dump(data, output, indent=2, ensure_ascii=False)
    print(f"Saved {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Crawl a ski resort website and produce a discovery report and draft static_infos.json."
    )
    parser.add_argument("url", help="Resort website URL (home page or any page on the site)")
    parser.add_argument("--resort-id", help="Resort slug (default: derived from the site name)")
    parser.add_argument("--name", help="Resort display name override")
    parser.add_argument("--country", help="Country override (default: derived from postal code)")
    parser.add_argument("--region", help="Region/province override (default: derived from postal code)")
    parser.add_argument("--continent", help="Continent override")
    parser.add_argument("--max-pages", type=int, default=150, help="Maximum HTML pages to fetch (default: 150)")
    parser.add_argument("--max-depth", type=int, default=4, help="Maximum link depth from the start URL (default: 4)")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests in seconds (default: 1.0)")
    parser.add_argument("--render", action="store_true", help="Render JavaScript-only pages with headless Chrome (Selenium)")
    parser.add_argument(
        "--output-dir",
        help="Output folder, relative to super-crawler/ unless it has a drive letter (default: output/<resortId>)",
    )
    args = parser.parse_args()

    start_url = normalize_url(args.url)
    fetcher = Fetcher(delay=args.delay)
    try:
        crawl_result = crawl(start_url, fetcher, args.max_pages, args.max_depth, args.render)
    finally:
        fetcher.close()
    if not crawl_result["pages"]:
        print(f"No pages fetched from {start_url}: {crawl_result['errors'][:3]}", file=sys.stderr)
        return 1

    discovery, static_infos = build_discovery(args, crawl_result, start_url, site_host(start_url))
    output_dir = resolve_output_dir(args.output_dir or f"output/{static_infos['resortId']}")
    write_json(output_dir / "discovery.json", discovery)
    write_json(output_dir / "static_infos.draft.json", static_infos)
    print(f"\nPages fetched: {len(crawl_result['pages'])}")
    for note in discovery["needsReview"]:
        print(f"  review: {note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
