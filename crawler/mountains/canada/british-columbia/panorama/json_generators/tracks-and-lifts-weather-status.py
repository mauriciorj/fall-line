import json
import os
import re
import time

import requests
from bs4 import BeautifulSoup
import truststore

truststore.inject_into_ssl()

RESORT_ID = "panorama"
SOURCE_URL = "https://www.panoramaresort.com/panorama-today/daily-snow-report#trailreport"
TRACKS = {
    "Champagne": [("World Cup Way", "blue"), ("Skyway", "blue"), ("Grice Paddy", "blue"), ("Rollercoaster", "blue"), ("Chute", "blue"), ("Skyline", "blue"), ("Liftline", "black"), ("Pod's", "black"), ("Tacky", "black"), ("Downhill", "black"), ("Cow's Face", "blue"), ("Millennium Black", "black"), ("Millennium Blue", "blue"), ("Elkhorn", "black"), ("Canadian Way - Upper", "blue"), ("Canadian Way - Lower", "blue"), ("Silky", "green")],
    "Discovery Zone": [("Highway 1", "green"), ("Stringer", "green"), ("Beginner", "green"), ("Campbell's Canyon", "green"), ("Canadian Discovery", "green"), ("Trapper's Ridge", "blue"), ("Trapper’s Lynx", "green")],
    "Extreme Dream Zone": [("Tombstone", "black"), ("Zone 2", "double black"), ("Gun Barrel", "double black"), ("Laresser Lane", "blue"), ("Trigger", "double black"), ("Elmo", "double black"), ("Orca", "double black"), ("Mocha", "double black"), ("Latte", "double black"), ("Cafe", "double black"), ("Champagne Surf", "double black"), ("Fat Chance", "double black"), ("Dunes", "double black"), ("First Chance", "black"), ("Pi", "double black"), ("Toadstool", "double black"), ("Surf", "double black"), ("Last Chance", "black"), ("Messerli's Mile", "blue")],
    "Founder's Ridge": [("Deck's Cross", "blue"), ("Madson's Mile", "blue"), ("McIntosh Way", "black"), ("Strobl Strasse", "blue"), ("Zehnder Way", "black"), ("Ostrander Alley", "blue"), ("Delesalle", "black"), ("Bell's Landing", "blue")],
    "Mile One": [("Powder Trail Green", "green"), ("Horseshoe", "green"), ("Showoff Blue", "blue"), ("Showoff Green", "green"), ("Powder Trail Blue", "blue"), ("Loose Moose", "blue"), ("Moose Trail", "green"), ("Old Timer", "blue"), ("Hay Fever", "black"), ("Secret Forest", "blue")],
    "Summit": [("Getmedown", "blue"), ("Top of the World", "black"), ("Tree Time", "black"), ("HLH", "black"), ("Tight Spots", "black"), ("Roy's Run", "black"), ("Outer Limits", "double black"), ("Picture Perfect", "blue"), ("Hideaway", "black"), ("Schober's Dream - Upper", "black"), ("Schober's Dream - Lower", "blue"), ("Schober's Glade", "blue"), ("View of 1000 Peaks", "black")],
    "Sun Bowl": [("Alive Glades", "blue"), ("Sunshine", "blue"), ("Sun Bowl Trail", "blue"), ("Sunburst", "blue"), ("Sundog", "blue"), ("Sunset", "blue"), ("Sunna", "blue"), ("Sunseeker", "blue"), ("Stump Farm", "blue"), ("C.F.I.", "black"), ("Marshall", "black"), ("Draino", "blue"), ("Lower Bowl", "blue"), ("Marker's Mark", "blue"), ("Solarium", "blue"), ("Sun's Out", "blue"), ("Village Way - Lower", "blue"), ("Village Way - Upper", "blue")],
    "Sunbird": [("Fritz's", "black"), ("Whiskey Jack", "black"), ("Chicken's Choice", "blue"), ("Sunbird", "black"), ("Triple Traverse", "green"), ("Heaven Can Wait - Upper", "blue"), ("Heaven Can Wait - Lower", "black"), ("Little Dipper - Upper", "blue"), ("Little Dipper - Lower", "black"), ("Out Rider", "green"), ("Detour", "blue"), ("Boomerang", "green")],
    "Taynton Bowl": [("Outback Ridge", "double black"), ("Heli High", "double black"), ("Heli Face", "double black"), ("Star Fire Cliffs", "double black"), ("Star Fire", "double black"), ("Cauldron", "double black"), ("White Room", "double black"), ("B-1st", "double black"), ("Donny B's", "double black"), ("Devil's Drop", "double black"), ("Ktunaxa", "double black"), ("C-Spine", "double black"), ("Stinger", "double black"), ("Kinbasket", "double black"), ("Whitetail", "double black"), ("Never Never Land", "double black"), ("Jekyll & Hyde", "double black"), ("The Monster", "double black"), ("Spectre", "double black"), ("Get Out!", "double black"), ("Ridgeback", "double black"), ("Funnel", "double black"), ("Landing Strip", "blue"), ("Taynton Trail", "blue"), ("Stash", "double black"), ("Yeti", "double black"), ("Paranormal", "double black"), ("Wild Thing", "double black"), ("Evasion Traverse", "double black"), ("Sidewinder Glades", "double black"), ("Stumbock's", "black"), ("Turnpike 1", "double black"), ("Sidebocks", "double black")],
    "Terrain Park": [("Stringer Park", "black"), ("Jib Park", "black"), ("Powder Trail Park", "black")],
    "Toby": [("Eagle Glide", "green"), ("New Timer", "blue"), ("2 Toby", "blue"), ("Over Easy", "blue"), ("Hoggs Flats", "green")],
}


def normalize_status(text):
    lower = text.lower()
    if "open" in lower:
        return "open"
    if "hold" in lower:
        return "on-hold"
    if "delay" in lower:
        return "delayed"
    if "close" in lower:
        return "closed"
    return "not informed"


def get_status():
    response = requests.get(SOURCE_URL.split("#")[0], headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    page_text = " ".join(soup.stripped_strings)
    tracks = []
    for area, definitions in TRACKS.items():
        for name, difficulty in definitions:
            match = re.search(re.escape(name) + r".{0,120}", page_text, re.IGNORECASE)
            tracks.append({"area": area, "name": name, "difficulty": difficulty, "status": normalize_status(match.group(0) if match else "")})
    return {"lifts": [], "tracks": tracks, "terrainParks": []}


def main():
    payload = {**get_status(), "resortId": RESORT_ID, "sourceUrl": SOURCE_URL, "updatedAt": int(time.time() * 1000)}
    output_file = os.path.join(os.path.dirname(__file__), "tracks-and-lifts-weather-status.json")
    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, ensure_ascii=False)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
