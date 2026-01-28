"""
server_loyalty.py (v33)
- Coupon issuance + usage event collection (offline-safe JSON store).
- Can be fed by store/landing-page events.
"""
from __future__ import annotations
from flask import Flask, request, jsonify
from pathlib import Path
from datetime import datetime, timedelta
import json, os, secrets

STATE_FILE = Path(os.environ.get("COUPON_STATE_FILE","./coupon_state.json"))
VISIT_FILE = Path(os.environ.get("VISIT_STATE_FILE","./visit_state.json"))

app = Flask(__name__)

def load_json(p: Path):
    if p.exists():
        try: return json.loads(p.read_text(encoding="utf-8"))
        except Exception: return {}
    return {}

def save_json(p: Path, obj: dict):
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

def issue(tier: str, length: int = 8) -> str:
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    code = "".join(secrets.choice(alphabet) for _ in range(length))
    st = load_json(STATE_FILE)
    st.setdefault("issued", {})
    st["issued"][code] = {"tier": tier, "issued_at": datetime.utcnow().isoformat(), "used": False}
    save_json(STATE_FILE, st)
    return code

@app.post("/coupon/issue")
def coupon_issue():
    data = request.get_json(force=True, silent=True) or {}
    tier = (data.get("tier") or "light").lower()
    code = issue(tier)
    return jsonify({"ok": True, "coupon_code": code, "tier": tier})

@app.post("/coupon/used")
def coupon_used():
    data = request.get_json(force=True, silent=True) or {}
    code = (data.get("coupon_code") or "").strip().upper()
    meta = data.get("meta") or {}
    st = load_json(STATE_FILE)
    if "issued" in st and code in st["issued"]:
        st["issued"][code]["used"] = True
        st["issued"][code]["used_at"] = datetime.utcnow().isoformat()
        st["issued"][code]["meta"] = meta
        save_json(STATE_FILE, st)
        return jsonify({"ok": True, "coupon_code": code})
    return jsonify({"ok": False, "error": "unknown coupon"}), 404

@app.post("/event/visit")
def visit():
    data = request.get_json(force=True, silent=True) or {}
    uid = (data.get("uid") or "anon")
    st = load_json(VISIT_FILE)
    st.setdefault("visits", [])
    st["visits"].append({"uid": uid, "ts": datetime.utcnow().isoformat(), "source": data.get("source","")})
    save_json(VISIT_FILE, st)
    return jsonify({"ok": True})

@app.get("/state")
def state():
    return jsonify({
        "coupons": load_json(STATE_FILE),
        "visits": load_json(VISIT_FILE),
        "coupon_state_file": str(STATE_FILE),
        "visit_state_file": str(VISIT_FILE),
    })



@app.post("/event/purchase")
def purchase():
    data = request.get_json(force=True, silent=True) or {}
    uid = (data.get("uid") or "anon")
    variant = data.get("variant","")
    amount = data.get("amount", 0)
    st = load_json(VISIT_FILE)
    st.setdefault("purchases", [])
    st["purchases"].append({"uid": uid, "variant": variant, "amount": amount, "ts": datetime.utcnow().isoformat()})
    save_json(VISIT_FILE, st)
    return jsonify({"ok": True})

@app.get("/report")
def report():
    st = load_json(VISIT_FILE)
    visits = st.get("visits", [])
    purchases = st.get("purchases", [])
    # unique visitors by variant
    vmap = {}
    for v in visits:
        var = v.get("variant","") or "A"
        uid = v.get("uid","anon")
        vmap.setdefault(var, set()).add(uid)
    pmap = {}
    for p in purchases:
        var = p.get("variant","") or "A"
        uid = p.get("uid","anon")
        pmap.setdefault(var, set()).add(uid)
    out = {}
    for var, uids in vmap.items():
        pu = pmap.get(var, set())
        out[var] = {"unique_visitors": len(uids), "unique_buyers": len(pu), "conv_rate": (len(pu)/len(uids) if len(uids) else 0.0)}
    return jsonify({"ok": True, "by_variant": out, "totals": {"visits": len(visits), "purchases": len(purchases)}})

@app.get("/retarget/list")
def retarget_list():
    """
    Returns UIDs to retarget: visited but not purchased within window minutes.
    """
    minutes = int(request.args.get("minutes", "60"))
    cutoff = datetime.utcnow() - timedelta(minutes=minutes)
    st = load_json(VISIT_FILE)
    visits = [v for v in st.get("visits", []) if v.get("ts")]
    purchases = st.get("purchases", [])
    purchased_uids = set([p.get("uid","") for p in purchases])
    target = []
    for v in visits:
        uid = v.get("uid","")
        if not uid or uid in purchased_uids:
            continue
        try:
            ts = datetime.fromisoformat(v["ts"].replace("Z",""))
        except Exception:
            continue
        if ts <= cutoff:
            target.append({"uid": uid, "variant": v.get("variant","A"), "source": v.get("source","")})
    # unique
    seen=set()
    uniq=[]
    for t in target:
        if t["uid"] in seen: continue
        seen.add(t["uid"]); uniq.append(t)
    return jsonify({"ok": True, "targets": uniq})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT","8090")))
