"""
server_webhook.py (v29)
- Receives store order webhooks and keeps a rolling 30-minute "buying now" counter in a local state file.
- This is a generic webhook receiver; adapt verification/signature to your store platform.
"""
from __future__ import annotations
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from pathlib import Path
import json
import os

STATE_FILE = Path(os.environ.get("WEBHOOK_STATE_FILE", "./live_counter_state.json"))
WINDOW_MIN = int(os.environ.get("WEBHOOK_WINDOW_MIN", "30"))

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

def prune(ts_list):
    now = datetime.utcnow()
    cutoff = now - timedelta(minutes=WINDOW_MIN)
    out = []
    for s in ts_list:
        try:
            t = datetime.fromisoformat(s)
        except Exception:
            continue
        if t >= cutoff:
            out.append(t.isoformat())
    return out

@app.post("/webhook/order")
def webhook_order():
    # NOTE: Add verification here (secret header, signature, etc.)
    state = load_state()
    ts_list = state.get("order_timestamps_utc", [])
    ts_list = prune(ts_list)
    ts_list.append(datetime.utcnow().isoformat())
    ts_list = prune(ts_list)
    state["order_timestamps_utc"] = ts_list
    state["last_30min_orders"] = len(ts_list)
    # "buying now" can be same as last_30min_orders, or smoothed.
    state["current_buying_now"] = len(ts_list)
    state["updated_at_utc"] = datetime.utcnow().isoformat()
    save_state(state)
    return jsonify({"ok": True, "current_buying_now": state["current_buying_now"], "last_30min_orders": state["last_30min_orders"]})

@app.get("/counter")
def counter():
    state = load_state()
    return jsonify({
        "current_buying_now": state.get("current_buying_now", 0),
        "last_30min_orders": state.get("last_30min_orders", 0),
        "updated_at_utc": state.get("updated_at_utc", ""),
        "state_file": str(STATE_FILE),
        "window_min": WINDOW_MIN,
    })

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8088"))
    app.run(host=host, port=port)
