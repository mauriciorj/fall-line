import json, os, re, time
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

RESORT_ID = "silverstar"
SOURCE_URL = "https://www.skisilverstar.com/the-mountain/hours-of-operation/"
DAYS = ("sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday")


def get_hours():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    browser = webdriver.Chrome(options=options)
    try:
        browser.get(SOURCE_URL)
        WebDriverWait(browser, 60).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        text = " ".join(browser.find_element("tag name", "body").text.split())
        match = re.search(
            r"(?:New Lift Hours|Lift Hours).*?(\d{1,2}:\d{2}\s*(?:am|pm)\s*(?:to|-)\s*\d{1,2}:\d{2}\s*(?:am|pm))",
            text,
            re.I,
        )
        if not match:
            raise ValueError("Could not find New Lift Hours in rendered HTML")
        return {day: match.group(1).lower() for day in DAYS}
    except WebDriverException:
        return {day: "closed" for day in DAYS}
    finally:
        browser.quit()


def main():
    payload = {
        "hours": get_hours(),
        "resortId": RESORT_ID,
        "sourceUrl": SOURCE_URL,
        "updatedAt": int(time.time() * 1000),
    }
    with open(
        os.path.join(os.path.dirname(__file__), "hours-of-operation.json"),
        "w",
        encoding="utf-8",
    ) as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
