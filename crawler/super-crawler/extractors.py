import json
import re
from urllib.parse import unquote, urljoin, urlsplit

from fetcher import url_tokens

WHITESPACE_RE = re.compile(r"\s+")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
EMAIL_IGNORE_RE = re.compile(
    r"\.(png|jpe?g|gif|webp|svg)$|@(example\.|sentry|wixpress|domain\.)", re.I
)
PHONE_RE = re.compile(
    r"(?<![\d$])(?:\+?1[\s.-]?)?\(?([2-9]\d{2})\)?[\s.-]?([2-9]\d{2})[\s.-]?(\d{4})(?!\d)"
)
CA_POSTAL_RE = re.compile(r"\b([ABCEGHJ-NPRSTVY])\d[A-Z][ -]?\d[A-Z]\d\b")
US_ZIP_RE = re.compile(r"\b[A-Z]{2}\s+\d{5}(?:-\d{4})?\b")
PRICE_RE = re.compile(r"\$\s?\d{1,4}(?:[.,]\d{2})?|\b\d{1,4}(?:[.,]\d{2})?\s?\$")
TIME_RE = re.compile(
    r"\b\d{1,2}(?::\d{2})?\s?(?:a\.?m\.?|p\.?m\.?)|\b\d{1,2}\s?h\s?\d{0,2}\b|\bclosed\b|\bfermé\b",
    re.I,
)
DAY_RE = re.compile(
    r"\b(mondays?|tuesdays?|wednesdays?|thursdays?|fridays?|saturdays?|sundays?|weekdays?|"
    r"weekends?|holidays?|lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche|fin de semaine)\b",
    re.I,
)
API_RE = re.compile(r"https?://[^\s\"'<>]+?(?:/api/|\.json)[^\s\"'<>]*")
TRAIL_CLASS_RE = re.compile(r"trail|piste|slope|\brun\b|lift|chair|remont", re.I)
DIFFICULTY_RE = re.compile(
    r"green|blue|black|diamond|double|beginner|intermediate|advanced|expert|easy|difficult|"
    r"facile|difficile|tr[eè]s difficile|vert|bleu|noir",
    re.I,
)
NEGATION_RE = re.compile(
    r"no longer|not offer|does not have|doesn't offer|discontinued|n'offre pas|n'offrons pas|plus offert",
    re.I,
)
JS_APP_MARKERS = (
    'id="__next"',
    "__NUXT__",
    "data-reactroot",
    'id="root"',
    'id="app"',
    "ng-version",
    "static.parastorage.com",
    "squarespace-cdn",
)
BUSINESS_TYPES = {
    "skiresort",
    "localbusiness",
    "organization",
    "touristattraction",
    "sportsactivitylocation",
    "place",
    "resort",
    "lodgingbusiness",
}
PROVINCES = {
    "A": "Newfoundland and Labrador",
    "B": "Nova Scotia",
    "C": "Prince Edward Island",
    "E": "New Brunswick",
    "G": "Quebec",
    "H": "Quebec",
    "J": "Quebec",
    "K": "Ontario",
    "L": "Ontario",
    "M": "Ontario",
    "N": "Ontario",
    "P": "Ontario",
    "R": "Manitoba",
    "S": "Saskatchewan",
    "T": "Alberta",
    "V": "British Columbia",
    "Y": "Yukon",
}
CATEGORY_KEYWORDS = {
    "contact": (
        "contact", "contact us", "nous joindre", "joindre", "find us", "directions",
        "getting here", "how to get here", "coordonnées",
    ),
    "hours": (
        "hours", "hours of operation", "operating hours", "opening hours", "schedule",
        "horaire", "horaires", "heures d'ouverture",
    ),
    "rates": (
        "lift ticket", "lift tickets", "tickets", "ticket", "rates", "prices", "pricing",
        "season pass", "season passes", "passes", "day pass", "billet", "billets", "tarif",
        "tarifs", "prix", "abonnement", "abonnements",
    ),
    "rentals": (
        "rental", "rentals", "rent", "equipment", "location", "location d'équipement",
        "équipement",
    ),
    "trails": (
        "trail", "trails", "trail map", "trail report", "trail status", "conditions",
        "snow report", "lift status", "mountain report", "activity report", "slopes", "runs",
        "piste", "pistes", "état des pistes", "conditions de ski",
    ),
    "lessons": (
        "lesson", "lessons", "ski school", "snow school", "snowsports school", "cours",
        "école", "ecole",
    ),
}
ACTIVITY_KEYWORDS = {
    "hasIceSkate": (
        "ice skating", "skating", "skate rink", "ice rink", "skating trail", "patin",
        "patinage", "patinoire",
    ),
    "hasCrossCountry": (
        "cross country", "cross-country", "nordic skiing", "nordic centre", "nordic center",
        "nordic trails", "ski de fond",
    ),
    "hasLessons": (
        "lesson", "lessons", "ski school", "snow school", "snowsports school", "cours de ski",
        "cours de planche", "école de ski", "ecole de ski",
    ),
    "hasSnowshoeing": ("snowshoe", "snowshoes", "snowshoeing", "raquette", "raquettes"),
    "hasSpa": ("spa", "nordic spa", "sauna", "massage", "massothérapie"),
    "hasTubing": (
        "tubing", "snow tubing", "tube park", "tubing park", "glissade sur tube", "glissades",
        "glissade",
    ),
    "hasZipline": ("zipline", "ziplines", "zip line", "zip lines", "zip-line", "tyrolienne", "tyroliennes"),
}


def keyword_pattern(words):
    alternatives = "|".join(sorted(map(re.escape, words), key=len, reverse=True))
    return re.compile(rf"(?<!\w)(?:{alternatives})(?!\w)", re.I)


CATEGORY_PATTERNS = {name: keyword_pattern(words) for name, words in CATEGORY_KEYWORDS.items()}
ACTIVITY_PATTERNS = {name: keyword_pattern(words) for name, words in ACTIVITY_KEYWORDS.items()}


def compact(text):
    return WHITESPACE_RE.sub(" ", text or "").strip()


def snippet(text, start, end, radius=60):
    return compact(text[max(0, start - radius) : end + radius])


def format_phone(area, exchange, line):
    return f"({area}) {exchange}-{line}"


def province_from_postal(postal_letter):
    return PROVINCES.get(postal_letter.upper())


def parse_json_ld(soup):
    nodes = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or script.get_text() or "")
        except ValueError:
            continue
        stack = [data]
        while stack:
            item = stack.pop()
            if isinstance(item, list):
                stack.extend(item)
            elif isinstance(item, dict):
                nodes.append(item)
                stack.extend(v for v in item.values() if isinstance(v, (dict, list)))
    return nodes


def node_types(node):
    value = node.get("@type", [])
    return {str(item).lower() for item in (value if isinstance(value, list) else [value])}


def format_postal_address(node):
    street = compact(str(node.get("streetAddress", "")))
    locality = compact(str(node.get("addressLocality", "")))
    region_postal = compact(f"{node.get('addressRegion', '')} {node.get('postalCode', '')}")
    return ", ".join(part for part in (street, locality, region_postal) if part)


def json_ld_facts(nodes):
    facts = {"addresses": [], "coordinates": [], "names": [], "openingHours": []}
    for node in nodes:
        types = node_types(node)
        if "postaladdress" in types:
            address = format_postal_address(node)
            if address:
                facts["addresses"].append(address)
        elif isinstance(node.get("address"), str) and types & BUSINESS_TYPES:
            facts["addresses"].append(compact(node["address"]))
        if "latitude" in node and "longitude" in node:
            try:
                facts["coordinates"].append(
                    {"lat": float(node["latitude"]), "lng": float(node["longitude"])}
                )
            except (TypeError, ValueError):
                pass
        if types & BUSINESS_TYPES and isinstance(node.get("name"), str):
            facts["names"].append(compact(node["name"]))
        for key in ("openingHours", "openingHoursSpecification"):
            if node.get(key):
                facts["openingHours"].append(node[key])
    return facts


def text_addresses(lines):
    addresses = []
    for index, line in enumerate(lines):
        match = CA_POSTAL_RE.search(line) or US_ZIP_RE.search(line)
        if not match or len(line) > 200:
            continue
        candidate = line
        if len(line) < 60 and index and re.match(r"^\d", lines[index - 1]):
            candidate = f"{lines[index - 1]}, {line}"
        addresses.append(candidate.strip(" |•·-–,"))
    return addresses


def extract_tables(soup, max_tables=5, max_rows=15):
    tables = []
    for table in soup.find_all("table"):
        rows = [
            [compact(cell.get_text(" ")) for cell in row.find_all(["th", "td"])]
            for row in table.find_all("tr")
        ]
        rows = [row for row in rows if any(row)]
        if len(rows) >= 2:
            tables.append(rows[:max_rows])
        if len(tables) >= max_tables:
            break
    return tables


def pattern_hits(pattern, value):
    return len(pattern.findall(value)) if value else 0


def analyze_page(url, soup, html):
    title = compact(soup.title.get_text()) if soup.title else ""
    site_name = soup.find("meta", attrs={"property": "og:site_name"})
    json_ld = json_ld_facts(parse_json_ld(soup))
    anchors = soup.find_all("a", href=True)
    hrefs = [anchor["href"].strip() for anchor in anchors]
    links = [
        (urljoin(url, href), compact(anchor.get_text(" "))[:120])
        for href, anchor in zip(hrefs, anchors)
    ]
    mailto = [
        unquote(href[7:].split("?")[0]).strip()
        for href in hrefs
        if href.lower().startswith("mailto:")
    ]
    tel = [href[4:] for href in hrefs if href.lower().startswith("tel:")]
    iframes = [urljoin(url, frame["src"]) for frame in soup.find_all("iframe", src=True)]
    script_count = len(soup.find_all("script"))
    inline_scripts = " ".join(
        script.string or "" for script in soup.find_all("script") if not script.get("src")
    )
    api_endpoints = sorted(set(API_RE.findall(inline_scripts)))[:20]
    js_marker = any(marker in html for marker in JS_APP_MARKERS)
    trail_elements = len(soup.find_all(class_=TRAIL_CLASS_RE))
    difficulty_markers = sum(
        1
        for image in soup.find_all(["img", "i", "span"])
        if DIFFICULTY_RE.search(f"{image.get('alt', '')} {' '.join(image.get('class', []))}")
    )

    for tag in soup(["script", "style", "noscript", "template", "svg"]):
        tag.decompose()
    headings = " | ".join(compact(h.get_text(" ")) for h in soup.find_all(["h1", "h2", "h3"]))
    text = compact(soup.get_text(" "))
    lines = [line for line in (compact(l) for l in soup.get_text("\n").splitlines()) if line]
    tokens = url_tokens(url)

    emails = [
        email
        for email in mailto + EMAIL_RE.findall(text)
        if EMAIL_RE.fullmatch(email) and not EMAIL_IGNORE_RE.search(email)
    ]
    phones = [("tel", format_phone(*m.groups())) for m in map(PHONE_RE.search, tel) if m]
    phones += [("text", format_phone(*m.groups())) for m in PHONE_RE.finditer(text)]

    categories = {
        name: {
            "url": pattern_hits(pattern, tokens),
            "title": pattern_hits(pattern, title),
            "headings": pattern_hits(pattern, headings),
            "body": pattern_hits(pattern, text),
        }
        for name, pattern in CATEGORY_PATTERNS.items()
    }

    activities = {}
    for name, pattern in ACTIVITY_PATTERNS.items():
        strong = bool(pattern.search(tokens) or pattern.search(title) or pattern.search(headings))
        matches = list(pattern.finditer(text))
        if not strong and not matches:
            continue
        snippets = [snippet(text, m.start(), m.end()) for m in matches[:2]]
        activities[name] = {
            "strong": strong,
            "mentions": len(matches),
            "negated": any(NEGATION_RE.search(item) for item in snippets),
            "snippets": snippets,
        }

    prices = list(PRICE_RE.finditer(text))
    hours_lines = [line[:200] for line in lines if DAY_RE.search(line) and TIME_RE.search(line)]

    return {
        "url": url,
        "title": title,
        "siteName": compact(site_name.get("content", "")) if site_name else "",
        "headings": headings[:500],
        "textLength": len(text),
        "needsJs": len(text) < 500 and (script_count >= 5 or js_marker),
        "links": links,
        "emails": emails,
        "phones": phones,
        "addresses": [("json-ld", a) for a in json_ld["addresses"]]
        + [("text", a) for a in text_addresses(lines)],
        "coordinates": json_ld["coordinates"],
        "names": json_ld["names"],
        "openingHours": json_ld["openingHours"],
        "categories": categories,
        "activities": activities,
        "priceCount": len(prices),
        "priceSnippets": [snippet(text, m.start(), m.end(), 50) for m in prices[:10]],
        "hoursSnippets": hours_lines[:10],
        "tables": extract_tables(soup),
        "trailElements": trail_elements,
        "difficultyMarkers": difficulty_markers,
        "iframes": iframes,
        "apiEndpoints": api_endpoints,
    }


def score_categories(page, anchor_text):
    scores = {}
    for name, hits in page["categories"].items():
        anchor_hits = pattern_hits(CATEGORY_PATTERNS[name], anchor_text)
        score = (
            5 * bool(hits["url"])
            + 4 * bool(hits["title"])
            + 3 * bool(hits["headings"])
            + 3 * bool(anchor_hits)
            + min(hits["body"], 5)
        )
        if name == "hours":
            score += 4 * min(len(page["hoursSnippets"]), 5)
        if not score:
            continue
        if name in ("rates", "rentals"):
            score += min(page["priceCount"], 10) / 2
        elif name == "trails":
            score += min(page["trailElements"] + page["difficultyMarkers"], 20) / 4
        scores[name] = round(score, 1)
    return scores


def link_priority(url, anchor_text, depth):
    value = f"{url_tokens(url)} {anchor_text}"
    return sum(bool(pattern.search(value)) for pattern in CATEGORY_PATTERNS.values()) * 10 + sum(
        bool(pattern.search(value)) for pattern in ACTIVITY_PATTERNS.values()
    ) * 3 - depth


def document_categories(url, anchor_text):
    value = f"{url_tokens(url)} {anchor_text} {urlsplit(url).path}"
    return [name for name, pattern in CATEGORY_PATTERNS.items() if pattern.search(value)]
