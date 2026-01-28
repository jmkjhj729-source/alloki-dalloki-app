from __future__ import annotations
from pathlib import Path
import json

from providers.kakao_i_alimtalk import send_kakao_i_alimtalk
from providers.solapi_sms import send_solapi_sms
from providers.instagram_dm import send_instagram_dm

def dispatch_send(sender: str, payload_path: Path, config_path: Path, dry_run: bool=False, fallback_sms_on_fail: bool=False):
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    cfg = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}

    def _ok(res) -> bool:
        if isinstance(res, dict):
            if res.get("dry_run"):
                return True
            # heuristics
            if res.get("ok") is True:
                return True
            if "error" in res:
                return False
        return True

    if sender == "kakao_i_alimtalk":
        try:
            res = send_kakao_i_alimtalk(payload, cfg.get("kakao_i_alimtalk", {}), dry_run=dry_run)
            if (not _ok(res)) and fallback_sms_on_fail and (not dry_run):
                fb = send_solapi_sms(payload, cfg.get("solapi_sms", {}), dry_run=dry_run)
                return {"channel": "kakao_i_alimtalk", "success": False, "result": res, "fallback": {"channel": "solapi_sms", "success": _ok(fb), "result": fb}}
            return {"channel": "kakao_i_alimtalk", "success": _ok(res), "result": res}
        except Exception as e:
            if fallback_sms_on_fail and (not dry_run):
                try:
                    fb = send_solapi_sms(payload, cfg.get("solapi_sms", {}), dry_run=dry_run)
                    return {"channel": "kakao_i_alimtalk", "success": False, "error": str(e), "fallback": {"channel": "solapi_sms", "success": _ok(fb), "result": fb}}
                except Exception as e2:
                    return {"channel": "kakao_i_alimtalk", "success": False, "error": str(e), "fallback": {"channel": "solapi_sms", "success": False, "error": str(e2)}}
            return {"channel": "kakao_i_alimtalk", "success": False, "error": str(e)}

    if sender == "solapi_sms":
        try:
            res = send_solapi_sms(payload, cfg.get("solapi_sms", {}), dry_run=dry_run)
            return {"channel": "solapi_sms", "success": _ok(res), "result": res}
        except Exception as e:
            return {"channel": "solapi_sms", "success": False, "error": str(e)}

    if sender == "instagram_dm":
        try:
            res = send_instagram_dm(payload, cfg.get("instagram_dm", {}), dry_run=dry_run)
            return {"channel": "instagram_dm", "success": _ok(res), "result": res}
        except Exception as e:
            return {"channel": "instagram_dm", "success": False, "error": str(e)}

    raise ValueError(f"Unknown sender: {sender}")
