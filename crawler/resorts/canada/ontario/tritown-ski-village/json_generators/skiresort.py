import json
import os
import re
import time
import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

PAGE_URL = "https://tritownskivillage.ca/"

def main():
    r = requests.get(PAGE_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30); r.raise_for_status(); text = " ".join(BeautifulSoup(r.content, "html.parser").get_text(" ", strip=True).split())
    vertical = re.search(r"approximately\s+([0-9]+[’']\s*of\s*vertical)", text, re.I)
    if not vertical: raise ValueError("Could not find vertical elevation in HTML")
    data = {"height": vertical.group(1).replace("’", "'")}
    with open(os.path.join(os.path.dirname(__file__), "skiresort.json"), "w", encoding="utf-8") as f: json.dump(data, f, indent=2)
if __name__ == "__main__": main()
