import json
import os
import re
import time

import requests
from bs4 import BeautifulSoup
import truststore

truststore.inject_into_ssl()

RESORT_ID = "sun-peaks-resort"
SOURCE_URL = "https://www.sunpeaksresort.com/ski-ride/weather-conditions-cams/lifts-trail-status"
TRAIL_GROUPS = {
    "Mt. Morrisey": {"green": "Anticipation,Downtown,Home Run,The Sticks", "blue": "Back In Time,C.C. Riders,Grand Return,I'Dunno,Mid-Life Crisis,Out Of The Woods,Second Growth,Shiner,Showboat,Still Smokin',Telly Gram", "black": "Agitator,Cover Shot,Lint Trap,Spin Cycle,Tumble Dry,Wringer,In Tatters,Static Cling"},
    "Orient Ridge": {"green": "East Village Ski Way,Main Village,Mt. Morrisey Connector,Orient Return,Trapper’s Lynx", "blue": "Ausfahrt,Ça M'a Fait Plaisir,Carpe Diem,Chikamichi,Cześć,Fair Dinkum,Hasta La Vista,Kia Ora", "off-trail": "Ca M'a Fait Plaisir Glades,Cześć Glades,Hasta La Vista Glades"},
    "Sundance": {"green": "Cowabunga,Gentle Giant,Home Instead,Homesteader Lower,Homesteader Upper,Moonbeam,Rambler,Sunbeam", "blue": "Grannie Greene's,Lone Fir Centre,Lone Fir West,PV X-Course,Sun Downer Lower,Sun Downer Upper,Sundance Lower,Sundance Upper,Sunrise,Three Bears Lower,Three Bears Upper", "black": "Peak-A-Boo", "free-style": "Terrain Park - Base Camp,Terrain Park - Basic Training,Terrain Park - Drop Zone,Terrain Park - Flight School", "off-trail": "Bug Out Glades,Grannie Greene's Glades,Lonesome Fir Glades,Three Bears Glades"},
    "Tod Mountain": {"green": "5 Mile Lower,5 Mile Upper,Burfield Outrun,Cahilty,Connector,Crystal Lane", "blue": "Alley,Blazer,Blue Line,Chute Lower,Cruiser Lower,Cruiser Upper,Crystal Run,Distributor,Exhibition Lower,Exhibition Upper,Fall Line,Gateway,Harry's Run,Hot Shot,Last Chance,Long Draw,Lunch Time,Munro Ridge Lower,Munro Ridge Upper,OSV,Quick Shot,Round-A-Bout,Runaway Lane,Saddle Up,Shortcut,The Other Way,The Spine,Trans Canada,West Bushwacker,Westsyde,Whyte's Ride", "black": "5th Avenue,Back Door,Black Line,Bluff,Broadway,Cariboo,Chief,Coquihalla,Crystal Bowl,East Bushwacker,Easy Out,Father Tom's,Front Door,Gil's Area,Hat Trick,Headwalls,Highway 22H,Highway 22A,Inner Gil's,Intimidator,Juniper Ridge,Little Headwalls,Main Face,Mid Mountain,Pink Flamingos,Ralph's Reach,Rice Bowl,Roller Coaster,Rollers,Short Draw,Skunk,Spillway,Sting,Sunny Side,Tighten Yer Boots,Toilet Bowl,White Rabbit,7 Mile Road", "double-black": "Challenger,Chute Upper,Expo,Freddy's,Green Door,Kookamungas,Offset", "off-trail": "Bling Glades,Bushwacker Glades,Cahilty Glades,Cariboo Glades,Chillway Glades,Coquihalla Glades,Cruiser Glades,Crystal Glades,Ralph's Reach Glades"},
}


def parse_tracks(html):
    soup = BeautifulSoup(html, "html.parser")
    text = " ".join(soup.stripped_strings)
    tracks = []
    for area, groups in TRAIL_GROUPS.items():
        for difficulty, names in groups.items():
            for name in names.split(","):
                match = re.search(re.escape(name) + r".{0,100}", text, re.IGNORECASE)
                status = "not informed"
                if match:
                    sample = match.group(0).lower()
                    status = "open" if "open" in sample else "closed" if "closed" in sample else "groomed" if "groomed" in sample else "not informed"
                tracks.append({"area": area, "name": name, "difficulty": difficulty, "status": status})
    return tracks


def get_status():
    response = requests.get(SOURCE_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    response.raise_for_status()
    return {"lifts": [], "tracks": parse_tracks(response.content.decode(response.encoding or "utf-8", errors="replace")), "terrainParks": []}


def main():
    payload = {**get_status(), "resortId": RESORT_ID, "sourceUrl": SOURCE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "tracks-and-lifts-weather-status.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
