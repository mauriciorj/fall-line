import json, subprocess, sys
from pathlib import Path
D=Path(__file__).parent; C=D.parents[1]; G=D/"snapshot_generator.py"; F=D/"snapshot_generator.json"
TABLES=("resorts","resortHours","resortRates","resortRentals","weatherAndStatus"); META={"resortId","sourceUrl","updatedAt"}; REQUIRED=("elevation","height","tracksGreenLength","tracksGreenProportion","tracksBlueLength","tracksBlueProportion","tracksBlackLength","tracksBlackProportion","tracksTotalLength")
sys.path.insert(0,str(C))
from convex_client import push_resort_hours,push_resort_rates,push_resort_rentals,push_ski_resorts,push_weather_and_status
def get_contents(s):
    c={x["table"]:x["content"] for x in s["tables"]}; missing=set(TABLES)-c.keys()
    if missing or c.keys()-set(TABLES): raise ValueError(f"Invalid snapshot tables: {sorted(missing)}")
    return c
def main():
    subprocess.run([sys.executable,str(G)],cwd=D,check=True); s=json.load(F.open(encoding="utf-8")); c=get_contents(s); r=c["resorts"]
    if s.get("resortId")!=r.get("resortId"): raise ValueError("Snapshot resort ID mismatch")
    if any(r.get(x) in (None,"") for x in REQUIRED): raise ValueError("Missing ski resort information")
    m={k:(c[k]["resortId"],c[k]["sourceUrl"],c[k]["updatedAt"]) for k in TABLES[1:]}
    if any(v[0]!=r["resortId"] for v in m.values()): raise ValueError("Table resort ID mismatch")
    h=c["resortHours"]["hours"]; h=[{"name":"Hours of operation","hours":[{"day":d,"time":t} for d,t in h.items()]}] if isinstance(h,dict) else h
    w={k:v for k,v in c["weatherAndStatus"].items() if k not in META}; w["trails"]=w.pop("tracks",[])
    return {"resorts":push_ski_resorts([r]),"resortHours":push_resort_hours(*m["resortHours"][:2],h,updated_at_ms=m["resortHours"][2]),"resortRates":push_resort_rates(*m["resortRates"][:2],c["resortRates"]["rates"],updated_at_ms=m["resortRates"][2]),"resortRentals":push_resort_rentals(*m["resortRentals"][:2],c["resortRentals"]["rentals"],updated_at_ms=m["resortRentals"][2]),"weatherAndStatus":push_weather_and_status(m["weatherAndStatus"][0],m["weatherAndStatus"][1],w,updated_at_ms=m["weatherAndStatus"][2])}
if __name__=="__main__":main()
