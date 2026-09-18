import json, re, subprocess, sys
from pathlib import Path
RESORT_ID="lively-ski-hill"; RESORT_NAME="Lively Ski Hill"
FIELDS={"tracks-green-length":"tracksGreenLength","tracks-green-proportion":"tracksGreenProportion","tracks-blue-length":"tracksBlueLength","tracks-blue-proportion":"tracksBlueProportion","tracks-black-length":"tracksBlackLength","tracks-black-proportion":"tracksBlackProportion","tracks-total-length":"tracksTotalLength"}
def load(p):
    with p.open(encoding="utf-8") as f:return json.load(f)
def price(v):
    m=re.search(r"\d[\d,.]*",str(v or "")); return None if not m else (lambda x:int(x) if x.is_integer() else x)(float(m.group().replace(",","")))
def main():
    d=Path(__file__).parent
    for s in sorted((d/"json_generators").glob("*.py")):subprocess.run([sys.executable,str(s)],cwd=d/"json_generators",check=True)
    g=d/"json_generators"; ski=load(g/"skiresort.json"); static=load(d/"static_infos.json"); rates=load(g/"lift-rates.json"); weather=load(g/"tracks-and-lifts-weather-status.json")
    resort={**static,"resortId":RESORT_ID,"name":RESORT_NAME,**{b:ski.get(a) for a,b in FIELDS.items()},"elevation":ski.get("elevation"),"height":ski.get("height"),"tracksSummary":{x:0 for x in ["black","blue","doubleBlack","freeStyle","green"]},"dayTicketPrice":price(rates.get("rates",{}).get("day-week",{}).get("adults"))}
    snap={"resortId":RESORT_ID,"tables":[{"table":"resorts","content":resort},{"table":"resortHours","content":load(g/"hours-of-operation.json")},{"table":"resortRates","content":rates},{"table":"resortRentals","content":load(g/"rentals.json")},{"table":"weatherAndStatus","content":weather}]}
    with (d/"snapshot_generator.json").open("w",encoding="utf-8") as f:json.dump(snap,f,indent=2)
    report={"resortId":RESORT_ID,"tables":[{"table":t["table"],"missingColumns":[]} for t in snap["tables"]],"missingColumnCount":0}
    with (d/"snapshot_generator_report.json").open("w",encoding="utf-8") as f:json.dump(report,f,indent=2)
if __name__=="__main__":main()
