import json, os, re
import truststore
truststore.inject_into_ssl()
import requests
from bs4 import BeautifulSoup
RESORT_INFO_URL="https://www.skiresort.com/en/ski-resort/adanac-ski-hill/"; TRACKS_INFO_URL="https://www.skiresort.com/en/ski-resort/adanac-ski-hill/slope-offering/"
def text(url):
    r=requests.get(url,headers={"User-Agent":"Mozilla/5.0"},timeout=30); r.raise_for_status(); return BeautifulSoup(r.content,"html.parser").get_text(" ",strip=True)
def main():
    info=text(RESORT_INFO_URL); slopes=text(TRACKS_INFO_URL)
    elevation=re.search(r"Elevation info\s+([0-9]+ m - [0-9]+ m).*?Difference\s+([0-9]+ m)",info,re.I)
    data={"elevation":elevation.group(1),"height":elevation.group(2)}
    for label,key in (("Easy","green"),("Intermediate","blue"),("Difficult","black")):
        m=re.search(rf"{label}\s+([0-9.]+ km).*?\(([0-9]+) %",slopes,re.I); data[f"tracks-{key}-length"]=m.group(1); data[f"tracks-{key}-proportion"]=m.group(2)
    data["tracks-total-length"]=re.search(r"Total:\s*([0-9.]+ km)",slopes,re.I).group(1)
    with open(os.path.join(os.path.dirname(__file__),"skiresort.json"),"w",encoding="utf-8") as output: json.dump(data,output,indent=2)
if __name__ == "__main__": main()
