import json, os, re, time
from datetime import date
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

RESORT_ID = "silverstar"
SOURCE_URL = "https://shop.skisilverstar.com/l/rentals/p/alp-rent"


def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)


def get_rentals():
    browser = driver()
    try:
        browser.get(SOURCE_URL)
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
            if not price:
                continue
            amount = re.search(r"\$\s*([0-9,]+)", price.get_text())
            if not amount:
                continue
            day = date(
                int(cell["data-year"]),
                int(cell["data-month"]) + 1,
                int(cell["data-date"]),
            )
            values.setdefault(
                "weekend" if day.weekday() >= 5 else "week",
                f"${amount.group(1).replace(',','')}",
            )
        return {
            "ski": {"adults": values.get("week")},
            "snowboard": {"adults": values.get("week")},
            "items": {},
        }
    except WebDriverException:
        return {"ski": {}, "snowboard": {}, "items": {}}
    finally:
        browser.quit()


def main():
    payload = {
        "rentals": get_rentals(),
        "resortId": RESORT_ID,
        "sourceUrl": SOURCE_URL,
        "updatedAt": int(time.time() * 1000),
    }
    with open(
        os.path.join(os.path.dirname(__file__), "rentals.json"), "w", encoding="utf-8"
    ) as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
