import json, os, time
RESORT_ID="lively-ski-hill"; SOURCE_URL="https://www.greatersudbury.ca/play/ski-hills/lively-ski-hill/"
def main():
    payload={"rates":{"day-week":{"adults":"$40"},"day-weekend":{"adults":"$40"}},"resortId":RESORT_ID,"sourceUrl":SOURCE_URL,"updatedAt":int(time.time()*1000)}
    with open(os.path.join(os.path.dirname(__file__),"lift-rates.json"),"w",encoding="utf-8") as output: json.dump(payload,output,indent=2,ensure_ascii=False)
if __name__ == "__main__": main()
