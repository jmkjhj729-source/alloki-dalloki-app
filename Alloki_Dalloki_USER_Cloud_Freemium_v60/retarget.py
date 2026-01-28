from __future__ import annotations
from pathlib import Path
from datetime import datetime, timedelta
import json

STATE = Path("./retarget_state.json")

def _load():
    return json.loads(STATE.read_text()) if STATE.exists() else {}

def _save(d):
    STATE.write_text(json.dumps(d, ensure_ascii=False, indent=2))

def record_visit(uid: str, ts: str):
    d=_load()
    d.setdefault(uid, {})["visit"]=ts
    _save(d)

def record_purchase(uid: str, ts: str):
    d=_load()
    d.setdefault(uid, {})["purchase"]=ts
    _save(d)

def find_retarget_targets(hours: int=24):
    d=_load()
    now=datetime.now()
    out=[]
    for uid,v in d.items():
        if "visit" in v and "purchase" not in v:
            t=datetime.fromisoformat(v["visit"])
            if now-t>=timedelta(hours=hours):
                out.append(uid)
    return out
