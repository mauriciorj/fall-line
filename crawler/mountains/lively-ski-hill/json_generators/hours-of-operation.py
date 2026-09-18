import json, os, time
SOURCE_URL = "https://www.greatersudbury.ca/play/ski-hills/lively-ski-hill/"
RESORT_ID = "lively-ski-hill"
def main():
    hours = {"sunday":"12:00pm to 4:30pm","monday":"closed","tuesday":"closed","wednesday":"closed","thursday":"closed","friday":"12:00pm to 4:30pm","saturday":"12:00pm to 4:30pm"}
    payload={"hours":hours,"resortId":RESORT_ID,"sourceUrl":SOURCE_URL,"updatedAt":int(time.time()*1000)}
    with open(os.path.join(os.path.dirname(__file__),"hours-of-operation.json"),"w",encoding="utf-8") as output: json.dump(payload,output,indent=2,ensure_ascii=False)
if __name__ == "__main__": main()
