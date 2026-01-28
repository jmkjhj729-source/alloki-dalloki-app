from __future__ import annotations
import requests, time, hmac, hashlib, base64

def _solapi_signature(api_secret: str, date: str, salt: str) -> str:
    msg = (date + salt).encode("utf-8")
    digest = hmac.new(api_secret.encode("utf-8"), msg, hashlib.sha256).digest()
    return base64.b64encode(digest).decode("utf-8")

def send_solapi_sms(payload: dict, cfg: dict, dry_run: bool=False):
    """
    SOLAPI SMS sender (example). Real endpoint may vary by region/account.
    You need api_key/api_secret/from_phone/to_phone.
    """
    message = payload.get("message_ko","")
    api_key = cfg.get("api_key","")
    api_secret = cfg.get("api_secret","")
    to = cfg.get("to_phone","")
    frm = cfg.get("from_phone","")

    date = str(int(time.time()*1000))
    salt = "s"
    sig = _solapi_signature(api_secret, date, salt)

    headers = {
        "Authorization": f"HMAC-SHA256 apiKey={api_key}, date={date}, salt={salt}, signature={sig}"
    }
    body = {
        "message": {
            "to": to,
            "from": frm,
            "text": message
        }
    }

    if dry_run:
        return {"dry_run": True, "headers": headers, "body": body}

    url = "https://api.solapi.com/messages/v4/send"
    r = requests.post(url, json=body, headers=headers, timeout=20)
    r.raise_for_status()
    return r.json()
