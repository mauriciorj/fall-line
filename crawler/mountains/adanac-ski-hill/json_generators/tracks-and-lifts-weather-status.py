import json, os, time
RESORT_ID="adanac-ski-hill"; SOURCE_URL="https://www.greatersudbury.ca/play/ski-hills/adanac-ski-hill/"
def main():
    payload={"lifts":[{"name":"New Quad","status":"closed"}],"tracks":[],"terrainParks":[],"resortId":RESORT_ID,"sourceUrl":SOURCE_URL,"updatedAt":int(time.time()*1000)}
    with open(os.path.join(os.path.dirname(__file__),"tracks-and-lifts-weather-status.json"),"w",encoding="utf-8") as output: json.dump(payload,output,indent=2)
if __name__ == "__main__": main()
