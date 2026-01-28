"""
retarget_worker.py (v38)
- Polls server_loyalty /retarget/list and sends retarget messages (Kakao/SMS).
Run via cron every 10-30 minutes.
"""
from __future__ import annotations
import json, time
from pathlib import Path
import requests
from send_dispatch import dispatch_send

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--server_base", type=str, default="http://127.0.0.1:8090")
    ap.add_argument("--minutes", type=int, default=60)
    ap.add_argument("--sender", choices=["kakao_i_alimtalk","solapi_sms"], default="solapi_sms")
    ap.add_argument("--config", type=str, default="./sender_config.json")
    ap.add_argument("--dry_run", action="store_true")
    ap.add_argument("--out_dir", type=str, default="./retarget_out")
    args = ap.parse_args()

    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)

    r = requests.get(args.server_base.rstrip("/") + "/retarget/list", params={"minutes": args.minutes}, timeout=20)
    r.raise_for_status()
    targets = r.json().get("targets", [])
    for t in targets:
        # build a minimal payload compatible with send_dispatch providers
        payload = {
            "platform": t.get("source",""),
            "segment": "retarget",
            "tier": "",
            "hook": "아직 혜택 남아있어요 🎁",
            "coupon_code": "",
            "bonus_link": "",
            "message_ko": "아직 혜택이 남아있어요 🎁 지금 들어오면 보너스 카드까지 열려요! 프로필 링크에서 확인해요.",
        }
        payload_path = out_dir / f"payload_{t.get('uid','anon')}.json"
        payload_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        res = dispatch_send(args.sender, payload_path, Path(args.config), dry_run=args.dry_run, fallback_sms_on_fail=False)
        print(t.get("uid"), res.get("success"), res.get("channel"))

if __name__ == "__main__":
    main()
