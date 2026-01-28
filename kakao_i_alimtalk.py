from __future__ import annotations
import requests

def send_kakao_i_alimtalk(payload: dict, cfg: dict, dry_run: bool=False):
    """
    Kakao i BizMessage (AlimTalk) sender.
    NOTE: Exact endpoints/fields differ by your BizMessage provider account.
    Docs: AlimTalk API requires OAuth2 token first (configure oauth_token_url).

    cfg required:
      - oauth_token_url, client_id, client_secret
      - base_url (send endpoint base)
      - sender_key, template_code, to_phone
    """
    message = payload.get("message_ko","")
    bonus_link = payload.get("bonus_link","")
    coupon = payload.get("coupon_code","")

    token_req = {
        "grant_type": "client_credentials",
        "client_id": cfg.get("client_id",""),
        "client_secret": cfg.get("client_secret",""),
    }
    send_req = {
        "to": cfg.get("to_phone",""),
        "senderKey": cfg.get("sender_key",""),
        "templateCode": cfg.get("template_code",""),
        "message": message,
        "variables": {
            "BONUS_LINK": bonus_link,
            "COUPON": coupon,
        },
    }

    if dry_run:
        return {"dry_run": True, "token_request": token_req, "send_request": send_req}

    # OAuth2
    tr = requests.post(cfg["oauth_token_url"], data=token_req, timeout=20)
    tr.raise_for_status()
    access_token = tr.json().get("access_token")
    if not access_token:
        raise RuntimeError("No access_token in oauth response")

    headers = {"Authorization": f"Bearer {access_token}"}
    # You must set your provider's real endpoint path:
    send_url = cfg["base_url"].rstrip("/") + "/bizmessage/v1/alimtalk/send"
    sr = requests.post(send_url, json=send_req, headers=headers, timeout=20)
    sr.raise_for_status()
    return sr.json()
