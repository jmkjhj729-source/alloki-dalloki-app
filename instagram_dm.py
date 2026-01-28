from __future__ import annotations
import requests

def send_instagram_dm(payload: dict, cfg: dict, dry_run: bool=False):
    """
    Instagram messaging send (example).
    Requires proper Meta permissions and a recipient IG-scoped ID.
    """
    token = cfg.get("page_access_token","")
    igsid = cfg.get("recipient_ig_scoped_id","")
    ver = cfg.get("api_version","v20.0")
    msg = payload.get("message_ko","")

    url = f"https://graph.facebook.com/{ver}/me/messages"
    body = {
        "recipient": {"id": igsid},
        "message": {"text": msg}
    }

    if dry_run:
        return {"dry_run": True, "url": url, "body": body}

    r = requests.post(url, params={"access_token": token}, json=body, timeout=20)
    r.raise_for_status()
    return r.json()
