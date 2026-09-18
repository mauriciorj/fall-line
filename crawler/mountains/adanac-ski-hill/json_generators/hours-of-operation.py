import json, os, time
SOURCE_URL = "https://www.greatersudbury.ca/play/ski-hills/adanac-ski-hill/"
RESORT_ID = "adanac-ski-hill"
def main():
    hours = {"sunday":"10:00am to 4:00pm","monday":"closed","tuesday":"closed","wednesday":"closed","thursday":"closed","friday":"10:00am to 4:00pm","saturday":"10:00am to 4:00pm"}
    payload={"hours":hours,"resortId":RESORT_ID,"sourceUrl":SOURCE_URL,"updatedAt":int(time.time()*1000)}
    with open(os.path.join(os.path.dirname(__file__),"hours-of-operation.json"),"w",encoding="utf-8") as output: json.dump(payload,output,indent=2,ensure_ascii=False)
if __name__ == "__main__": main()
