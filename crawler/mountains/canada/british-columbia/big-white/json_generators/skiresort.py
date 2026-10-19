import json
import os
import time

RESORT_ID = "big-white"
SOURCE_URL = "https://www.skiresort.com/en/ski-resort/big-white/"


def get_ski_resort_info():
    return {}


def main():
    with open(os.path.join(os.path.dirname(__file__), "skiresort.json"), "w", encoding="utf-8") as output:
        json.dump(get_ski_resort_info(), output, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
