import json
import os
import re
import time
from datetime import date

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

RESORT_ID = "sun-peaks-resort"
URLS = {
    "day": "https://store.sunpeaksresort.com/l/winter-tickets/c/alpine-day-tickets",
    "afternoon": "https://store.sunpeaksresort.com/l/winter-tickets/c/alpine-afternoon-tickets",
}


def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)


def parse_calendar(html):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    values = {}
    for cell in soup.select(".air-datepicker-cell.enhanced-calendar:not(.disabled)"):
        price = cell.select_one(".price-major")
        if not price or not re.search(r"\$\s*[0-9]", price.get_text()):
            continue
        try:
            current = date(
                int(cell["data-year"]),
                int(cell["data-month"]) + 1,
                int(cell["data-date"]),
            )
        except (KeyError, ValueError):
            continue
        amount = re.search(r"\$\s*([0-9,]+)", price.get_text())
        if amount:
            values.setdefault(
                "weekend" if current.weekday() >= 5 else "week",
                f"${amount.group(1).replace(',', '')}",
            )
    return values


def get_lift_rates():
    driver = get_driver()
    try:
        rates = {}
        for period, url in URLS.items():
            driver.get(url)
            WebDriverWait(driver, 30).until(
                lambda current: "air-datepicker-cell" in current.page_source
            )
            values = parse_calendar(driver.page_source)
            if values.get("week"):
                rates[f"{period}-week"] = {"adults": values["week"]}
            if values.get("weekend"):
                rates[f"{period}-weekend"] = {"adults": values["weekend"]}
        return rates
    except WebDriverException:
        return {}
    finally:
        driver.quit()


def main():
    payload = {
        "rates": get_lift_rates(),
        "resortId": RESORT_ID,
        "sourceUrl": URLS["day"],
        "updatedAt": int(time.time() * 1000),
    }
    output_file = os.path.join(os.path.dirname(__file__), "lift-rates.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
