import json, os, re, time
import requests
from bs4 import BeautifulSoup
import truststore

truststore.inject_into_ssl()
RESORT_ID = "silverstar"
SOURCE_URL = (
    "https://www.skisilverstar.com/the-mountain/weather-conditions/lift-trail-status/"
)
TRACKS = {
    "Attridge / Vance Creek / Silver Woods": {
        "green": "Criss Cross,Comet Trail,Hursin' Around,Main Street Skiway,Far Out,Over the Hill,Last Chance,Silver Fox,Bergerstrasse,Ab erdeen Skiway,Easy Street",
        "blue": "Abbott's Gulch,Split Decision,Solitude,Home Run,Ridge Run,Milky Way,Exhibition,Big Dipper,Middle Dipper,Little Dipper,Lower Exhibition,East Off,Walt's Run,Whiskey Jack,Sundance,Spence Meadows,Silver Meadows,Trinity Trees,Robson Street,Eldorado,Sunny High,25 North,Roller Coaster,Robin's Hood,North Star,Star Struck,Sherwood Forest,Shooting Star,Baker's Acres",
        "black": "Outback,Fastback,Soreback,Bushback,Ridgeback,Attridge Face,Moonbeam,Bib's Bumps,Southern Cross,Chute,Show Off,Hot Dog,Chalet Alley,Gopher Glades,Mine Shaft,Glade Runner,Chaos",
    },
    "Putnam Creek / Backside": {
        "blue": "Focus Peak,Sunny Ridge",
        "black": "Davidson's Delight,Uncle Buck,Huckleberry,Hunk With We Willie,Pipeline,Can Man Do,Morris Maxit,Gong Show,Quick Silver,High Lead,Chute 5,Kasanova,Rusty Whistle,Head Wall,Abbey Road,Three Wise Men,Doose Bob,Caliper Ridge,Normania,Nirvana,Paradise Glades,Cudd's Run,Northern Lights,Raven,Hinky Heights,Sunny Glades,Campbell's Loop,Leash,Black Bear,Muerte,Holy Smokes,Spirit Bowl,Bon Diablo,Free Fall,White Elephant,Where's Bob,Stardust,Here's Joe,Black Pine,Bobtail's Rush,Zipper,Blue Moon,No Knees,Eldorado Bumps",
    },
}


def get_status():
    response = requests.get(
        SOURCE_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30
    )
    response.raise_for_status()
    text = " ".join(BeautifulSoup(response.content, "html.parser").stripped_strings)
    tracks = []
    for area, groups in TRACKS.items():
        for difficulty, names in groups.items():
            for name in names.split(","):
                match = re.search(re.escape(name) + r".{0,100}", text, re.I)
                sample = match.group(0).lower() if match else ""
                status = (
                    "open"
                    if "open" in sample
                    else "closed" if "closed" in sample else "not informed"
                )
                tracks.append(
                    {
                        "area": area,
                        "name": name,
                        "difficulty": difficulty,
                        "status": status,
                    }
                )
    return {"lifts": [], "tracks": tracks, "terrainParks": []}


def main():
    payload = {
        **get_status(),
        "resortId": RESORT_ID,
        "sourceUrl": SOURCE_URL,
        "updatedAt": int(time.time() * 1000),
    }
    with open(
        os.path.join(os.path.dirname(__file__), "tracks-and-lifts-weather-status.json"),
        "w",
        encoding="utf-8",
    ) as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
