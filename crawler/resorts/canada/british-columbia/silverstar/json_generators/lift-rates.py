import json, os, re, time
from datetime import date
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait

RESORT_ID = "silverstar"
URL = "https://store.skisilverstar.com/l/winter-tickets/c/alpine-tickets"


def get_rates():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    browser = webdriver.Chrome(options=options)
    try:
        browser.get(URL)
        WebDriverWait(browser, 60).until(
            lambda d: "air-datepicker-cell" in d.page_source
        )
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(browser.page_source, "html.parser")
        values = {}
        for cell in soup.select(
            ".air-datepicker-cell.enhanced-calendar:not(.disabled)"
        ):
            price = cell.select_one(".price-major")
            amount = re.search(r"\$\s*([0-9,]+)", price.get_text()) if price else None
            if amount:
                day = date(
                    int(cell["data-year"]),
                    int(cell["data-month"]) + 1,
                    int(cell["data-date"]),
                )
                values.setdefault(
                    "day-weekend" if day.weekday() >= 5 else "day-week",
                    {
                        "adults": f"${amount.group(1).replace(',','')}",
                        "seniors": f"${amount.group(1).replace(',','')}",
                        "youth": f"${amount.group(1).replace(',','')}",
                    },
                )
        return values
    except WebDriverException:
        return {}
    finally:
        browser.quit()


def main():
    payload = {
        "rates": get_rates(),
        "resortId": RESORT_ID,
        "sourceUrl": URL,
        "updatedAt": int(time.time() * 1000),
    }
    with open(
        os.path.join(os.path.dirname(__file__), "lift-rates.json"),
        "w",
        encoding="utf-8",
    ) as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
