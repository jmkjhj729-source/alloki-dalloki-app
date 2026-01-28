"""
server_webhook_platforms.py (v30)
- Platform-specific webhook parsing with verification stubs.
- Maintains rolling counters for 5min and 30min and detects high-amount orders.
"""
from __future__ import annotations
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from pathlib import Path
import json, os

STATE_FILE = Path(os.environ.get("WEBHOOK_STATE_FILE","./live_counter_state.json"))
WINDOW_5 = 5
WINDOW_30 = 30
HIGH_AMOUNT_THRESHOLD = int(os.environ.get("HIGH_AMOUNT_THRESHOLD","50000"))

app = Flask(__name__)

def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

def prune(ts_list, minutes):
    now = datetime.utcnow()
    cutoff = now - timedelta(minutes=minutes)
    out = []
    for rec in ts_list:
        try:
            t = datetime.fromisoformat(rec["ts"])
        except Exception:
            continue
        if t >= cutoff:
            out.append(rec)
    return out

def minute_bins(orders, minutes:int):
    """
    Return list of length `minutes` with per-minute counts ending at now (UTC).
    Index -1 is current minute bucket.
    """
    now = datetime.utcnow().replace(second=0, microsecond=0)
    buckets = [0]*minutes
    for o in orders:
        try:
            t = datetime.fromisoformat(o["ts"]).replace(tzinfo=None)
        except Exception:
            continue
        dtm = t.replace(second=0, microsecond=0)
        diff = int((now - dtm).total_seconds()//60)
        if 0 <= diff < minutes:
            buckets[minutes-1-diff] += 1
    return buckets

def sum_amount(orders):
    s = 0
    for o in orders:
        try: s += int(o.get("amount",0))
        except Exception: pass
    return s

def record(amount_krw: int):
    state = load_state()
    lst = state.get("orders", [])
    lst.append({"ts": datetime.utcnow().isoformat(), "amount": int(amount_krw)})
    lst5 = prune(lst, WINDOW_5)
    lst30 = prune(lst, WINDOW_30)
    state["orders"] = lst30  # keep 30-min window
    state["count_5min"] = len(lst5)
    state["count_30min"] = len(lst30)
    
state["sum_5min"] = sum_amount(lst5)
state["sum_30min"] = sum_amount(lst30)
state["bins_30min"] = minute_bins(lst30, 30)
state["bins_5min"] = minute_bins(lst5, 5)
state["last_amount"] = int(lst30[-1].get("amount",0)) if lst30 else 0
state["last_order_at_utc"] = lst30[-1]["ts"] if lst30 else ""
state["high_amount_hit"] = any(o.get("amount",0) >= HIGH_AMOUNT_THRESHOLD for o in lst30)
# "recent high amount" = within last 2 minutes
try:
    state["high_amount_recent"] = any(
        (datetime.utcnow() - datetime.fromisoformat(o["ts"])).total_seconds() <= 120 and o.get("amount",0) >= HIGH_AMOUNT_THRESHOLD
        for o in lst30
    )
except Exception:
    state["high_amount_recent"] = False
    state["updated_at_utc"] = datetime.utcnow().isoformat()
    save_state(state)
    return state

# ---- Platform parsers ----
def parse_smartstore(payload: dict) -> int:
    # Example: payload["order"]["payment"]["totalAmount"]
    return int(payload.get("order",{}).get("payment",{}).get("totalAmount",0))

def parse_tosspay(payload: dict) -> int:
    # Example: payload["totalAmount"]
    return int(payload.get("totalAmount",0))

def parse_cafe24(payload: dict) -> int:
    # Example: payload["orders"][0]["payment_amount"]
    orders = payload.get("orders",[])
    if orders:
        return int(orders[0].get("payment_amount",0))
    return 0

@app.post("/webhook/<platform>")
def webhook(platform):
    payload = request.get_json(force=True, silent=True) or {}
    # TODO: verify signatures per platform
    if platform == "smartstore":
        amount = parse_smartstore(payload)
    elif platform == "tosspay":
        amount = parse_tosspay(payload)
    elif platform == "cafe24":
        amount = parse_cafe24(payload)
    else:
        return jsonify({"ok": False, "error": "unknown platform"}), 400
    state = record(amount)
    return jsonify({"ok": True, "platform": platform, "amount": amount, **state})

@app.get("/counter")
def counter():
    return jsonify(load_state())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT","8089")))
