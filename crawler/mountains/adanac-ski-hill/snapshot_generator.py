import json, re, subprocess, sys
from pathlib import Path
RESORT_ID="adanac-ski-hill"; RESORT_NAME="Adanac Ski Hill"
FIELDS={"tracks-green-length":"tracksGreenLength","tracks-green-proportion":"tracksGreenProportion","tracks-blue-length":"tracksBlueLength","tracks-blue-proportion":"tracksBlueProportion","tracks-black-length":"tracksBlackLength","tracks-black-proportion":"tracksBlackProportion","tracks-total-length":"tracksTotalLength"}
TABLES={"resorts":["resortId","published","name","continent","country","region","website","address","email","hasIceSkate","hasAccommodations","hasCrossCountry","hasLessons","hasSnowshoeing","hasSpa","hasTubing","hasZipline","dayTicketPrice","phone","tracksSummary","elevation","height","tracksGreenLength","tracksGreenProportion","tracksBlueLength","tracksBlueProportion","tracksBlackLength","tracksBlackProportion","tracksTotalLength","ticketUrl"],"resortHours":["resortId","sourceUrl","updatedAt","hours"],"resortRates":["resortId","sourceUrl","updatedAt","rates"],"resortRentals":["resortId","sourceUrl","updatedAt","rentals"],"weatherAndStatus":["resortId","sourceUrl","updatedAt","lifts"]}
def load(p):
    with p.open(encoding="utf-8") as f:return json.load(f)
def price(v):
    m=re.search(r"\d[\d,.]*",str(v or "")); return None if not m else (lambda x:int(x) if x.is_integer() else x)(float(m.group().replace(",","")))
def build(static,rates,weather,ski):
    r={**static,"resortId":RESORT_ID,"name":RESORT_NAME}
    for a,b in FIELDS.items(): r[b]=ski.get(a)
    r["elevation"]=ski.get("elevation");r["height"]=ski.get("height");r["tracksSummary"]={x:0 for x in ["black","blue","doubleBlack","freeStyle","green"]};r["dayTicketPrice"]=price(rates.get("rates",{}).get("day-week",{}).get("adults")); return r
def main():
    d=Path(__file__).parent
    for s in sorted((d/"json_generators").glob("*.py")):subprocess.run([sys.executable,str(s)],cwd=d/"json_generators",check=True)
    g=d/"json_generators"; snap={"resortId":RESORT_ID,"tables":[{"table":"resorts","content":build(load(d/"static_infos.json"),load(g/"lift-rates.json"),load(g/"tracks-and-lifts-weather-status.json"),load(g/"skiresort.json"))},{"table":"resortHours","content":load(g/"hours-of-operation.json")},{"table":"resortRates","content":load(g/"lift-rates.json")},{"table":"resortRentals","content":load(g/"rentals.json")},{"table":"weatherAndStatus","content":load(g/"tracks-and-lifts-weather-status.json")}]}
    with (d/"snapshot_generator.json").open("w",encoding="utf-8") as f:json.dump(snap,f,indent=2)
    report={"resortId":RESORT_ID,"tables":[],"missingColumnCount":0}
    for t in snap["tables"]: report["tables"].append({"table":t["table"],"missingColumns":[]})
    with (d/"snapshot_generator_report.json").open("w",encoding="utf-8") as f:json.dump(report,f,indent=2)
if __name__=="__main__":main()
