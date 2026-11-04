import re
import time
import warnings
from urllib.parse import parse_qsl, unquote, urlencode, urlsplit, urlunsplit
from urllib.robotparser import RobotFileParser

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

USER_AGENT = "Mozilla/5.0 (compatible; FallLineSuperCrawler/1.0)"
LANG_PREFIXES = {"en", "fr", "es", "de", "it", "pt", "nl", "ja", "zh", "ko"}
TRACKING_PARAMS = re.compile(r"^(utm_.*|fbclid|gclid|mc_cid|mc_eid|_ga|ref)$", re.I)
ASSET_EXTENSIONS = re.compile(
    r"\.(jpe?g|png|gif|webp|avif|svg|ico|bmp|css|js|mjs|map|mp4|m4v|mov|avi|webm|mp3|wav|"
    r"zip|rar|7z|gz|docx?|xlsx?|pptx?|ics|xml|json|rss|woff2?|ttf|otf|eot)$",
    re.I,
)
DOCUMENT_EXTENSIONS = re.compile(r"\.pdf$", re.I)
SKIP_PATHS = re.compile(
    r"/(blog|blogs|news|nouvelles|press|tag|tags|category|categories|categorie|author|auteur|"
    r"feed|wp-json|wp-admin|wp-login\.php|wp-content|cart|panier|checkout|login|logout|"
    r"account|my-account|compte|search|recherche|cdn-cgi)(/|$)|/page/\d+/?$",
    re.I,
)


def site_host(url):
    host = urlsplit(url).hostname or ""
    return host[4:] if host.startswith("www.") else host


def origin(url):
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}"


def lang_prefix(url):
    segments = [segment for segment in urlsplit(url).path.split("/") if segment]
    first = segments[0].lower() if segments else ""
    return first if first in LANG_PREFIXES else None


def normalize_url(url):
    parts = urlsplit(url.strip())
    query = urlencode(
        [(k, v) for k, v in parse_qsl(parts.query) if not TRACKING_PARAMS.match(k)]
    )
    return urlunsplit(
        (parts.scheme.lower(), parts.netloc.lower(), parts.path or "/", query, "")
    )


def url_key(url):
    parts = urlsplit(url)
    return f"{site_host(url)}{parts.path.rstrip('/') or '/'}?{parts.query}"


def url_tokens(url):
    parts = urlsplit(url)
    return re.sub(r"[-_/.+=&?]+", " ", unquote(f"{parts.path} {parts.query}")).strip()


def is_document(url):
    return bool(DOCUMENT_EXTENSIONS.search(urlsplit(url).path))


def skip_reason(url, host, start_lang):
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https"):
        return "scheme"
    if site_host(url) != host:
        return "offsite"
    if ASSET_EXTENSIONS.search(parts.path):
        return "asset"
    if SKIP_PATHS.search(parts.path):
        return "pattern"
    lang = lang_prefix(url)
    if lang and lang != start_lang:
        return "language"
    return None


class Fetcher:
    def __init__(self, delay=1.0, timeout=30, render_wait=3.0):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.delay = delay
        self.timeout = timeout
        self.render_wait = render_wait
        self.robots = {}
        self._last_request = 0.0
        self._driver = None

    def _throttle(self):
        wait = self.delay - (time.monotonic() - self._last_request)
        if wait > 0:
            time.sleep(wait)
        self._last_request = time.monotonic()

    def get(self, url):
        self._throttle()
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response

    def robots_for(self, url):
        site = origin(url)
        if site not in self.robots:
            parser = RobotFileParser()
            try:
                parser.parse(self.get(f"{site}/robots.txt").text.splitlines())
            except requests.RequestException:
                parser.parse([])
            self.robots[site] = parser
        return self.robots[site]

    def allowed(self, url):
        return self.robots_for(url).can_fetch(USER_AGENT, url)

    def sitemap_urls(self, start_url, limit=1000, max_sitemaps=20):
        site = origin(start_url)
        queue = list(self.robots_for(start_url).site_maps() or []) or [
            f"{site}/sitemap.xml",
            f"{site}/sitemap_index.xml",
        ]
        urls, visited = [], set()
        while queue and len(visited) < max_sitemaps and len(urls) < limit:
            sitemap = queue.pop(0)
            if sitemap in visited:
                continue
            visited.add(sitemap)
            try:
                soup = BeautifulSoup(self.get(sitemap).content, "html.parser")
            except requests.RequestException:
                continue
            target = queue if soup.find("sitemapindex") else urls
            target.extend(loc.get_text(strip=True) for loc in soup.find_all("loc"))
        return urls[:limit]

    def render_html(self, url):
        if self._driver is None:
            from selenium import webdriver

            options = webdriver.ChromeOptions()
            for argument in ("--headless=new", "--no-sandbox", "--disable-dev-shm-usage"):
                options.add_argument(argument)
            options.add_argument(f"--user-agent={USER_AGENT}")
            self._driver = webdriver.Chrome(options=options)
            self._driver.set_page_load_timeout(self.timeout)
        self._throttle()
        self._driver.get(url)
        time.sleep(self.render_wait)
        return self._driver.page_source

    def close(self):
        if self._driver is not None:
            self._driver.quit()
            self._driver = None
        self.session.close()
