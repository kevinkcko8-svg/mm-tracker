import csv, json, os
from datetime import datetime, timedelta, timezone
from pathlib import Path
import requests
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE=Path(__file__).parent
ME="Even_is_Even"
RIVALS=["Anatellia","Sam","cinnmn"]
FIELDS=["wins","kills","deaths","games_played","coins"]
KEYS={"wins":["wins"],"kills":["kills"],"deaths":["deaths"],"games_played":["games","games_played"],"coins":["coins"]}
self_path=BASE/"data/history.csv"
rival_path=BASE/"data/rivals.csv"
state_path=BASE/"data/alert_state.json"
alerts_path=BASE/"data/pending_alerts.json"

def load(path):
    if not path.exists(): return []
    with path.open(newline="",encoding="utf-8") as f: return list(csv.DictReader(f))

def save(path,rows,columns):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=columns,extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

def stats(name):
    if not os.getenv("HYPIXEL_API_KEY"): raise RuntimeError("Missing HYPIXEL_API_KEY")
    s=requests.Session()
    r=s.get("https://api.minecraftservices.com/minecraft/profile/lookup/name/"+name,timeout=25)
    r.raise_for_status()
    r=s.get("https://api.hypixel.net/v2/player",params={"uuid":r.json()["id"]},
            headers={"API-Key":os.environ["HYPIXEL_API_KEY"]},timeout=30)
    r.raise_for_status()
    p=r.json()
    if not p.get("success") or not p.get("player"): raise RuntimeError(str(p.get("cause","No player")))
    d=(p["player"].get("stats") or {}).get("MurderMystery") or {}
    out={k:next((int(d[x]) for x in keys if type(d.get(x)) in (int,float)),"") for k,keys in KEYS.items()}
    if out["wins"]=="": raise RuntimeError("Missing MurderMystery wins for "+name)
    return out

def ts(row): return datetime.fromisoformat(row["timestamp_utc"].replace("Z","+00:00"))

def gain24(rows,now):
    rows=[r for r in rows if r.get("wins","")!="" and ts(r)<=now]
    if not rows: return None
    end=max(rows,key=ts)
    if now-ts(end)>timedelta(hours=8): return None
    target=ts(end)-timedelta(hours=24)
    old=min(rows,key=lambda r:abs(ts(r)-target))
    if abs(ts(old)-target)>timedelta(hours=2): return None
    return int(end["wins"])-int(old["wins"])

def make_charts(rows):
    for suffix,filename in [("","totals.png"),("_delta","changes.png")]:
        fig,ax=plt.subplots(figsize=(11,5))
        for k in ["wins","kills","deaths","games_played"]:
            dots=[(ts(r),int(r[k+suffix])) for r in rows if r.get(k+suffix,"")!=""]
            if dots: ax.plot([a for a,b in dots],[b for a,b in dots],label=k)
        ax.set_title(ME+" Murder Mystery "+("totals" if not suffix else "changes"))
        ax.set_xlabel("Time (UTC)")
        ax.grid(alpha=.25); ax.legend()
        fig.autofmt_xdate(); fig.tight_layout()
        fig.savefig(BASE/filename,dpi=160); plt.close(fig)

def main():
    now=datetime.now(timezone.utc)
    stamp=now.isoformat(timespec="seconds")
    own=load(self_path)
    record={"timestamp_utc":stamp,**stats(ME)}
    prev=own[-1] if own else {}
    for k in FIELDS:
        record[k+"_delta"]=int(record[k])-int(prev[k]) if record[k]!="" and prev.get(k,"")!="" else ""
    own.append(record)
    save(self_path,own,["timestamp_utc",*FIELDS,*[k+"_delta" for k in FIELDS]])
    rivals=load(rival_path)
    if True:  # All four players are sampled on every scheduled or manual run
        for name in RIVALS:
            try:
                rivals.append({"timestamp_utc":stamp,"player":name,**stats(name)})
                print("Rival sampled:",name)
            except Exception as e:
                print("Rival unavailable:",name,str(e))
        if rivals: save(rival_path,rivals,["timestamp_utc","player",*FIELDS])
    states=json.loads(state_path.read_text()) if state_path.exists() else {}
    alerts=[]
    my_gain=gain24(own,now)
    for name in RIVALS:
        their_gain=gain24([r for r in rivals if r["player"].lower()==name.lower()],now)
        if my_gain is None or their_gain is None: continue
        ahead=their_gain>my_gain
        if name in states and states[name] is False and ahead:
            alerts.append({"player":name,"self_gain":my_gain,"rival_gain":their_gain,"at":stamp})
        states[name]=ahead
    state_path.parent.mkdir(parents=True,exist_ok=True)
    state_path.write_text(json.dumps(states,indent=2)+"\n")
    alerts_path.write_text(json.dumps(alerts,indent=2)+"\n")
    print("Own totals:",record,"Alerts:",alerts)
    make_charts(own)

if __name__=="__main__": main()
