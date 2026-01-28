from __future__ import annotations
from pathlib import Path
import json

def build_comment_reply_payload(payload: dict, platform: str) -> dict:
    """
    Generates a safe "comment reply" script and pinned comment copy.
    This does NOT post automatically (platform APIs are limited). Intended for Zapier/Make/manual posting.
    """
    bonus = payload.get("bonus_link","")
    coupon = payload.get("coupon_code","")
    hook = payload.get("hook","")
    if platform.lower() == "tiktok":
        pinned = f"{hook} 👉 프로필 링크에서 시즌팩 확인! (쿠폰 {coupon})"
        reply = f"댓글 남겨줘서 고마워요! 😊 프로필 링크로 들어가면 보너스 카드도 있어요 🎁 (쿠폰 {coupon})"
    else:
        pinned = f"{hook} 🔗 링크로 바로 이동! (쿠폰 {coupon})"
        reply = f"DM 대신 링크로 안내해요 🐶🌈 보너스 카드 확인: {bonus} (쿠폰 {coupon})"
    return {"platform": platform, "pinned_comment": pinned, "reply_template": reply}

def build_landing_payload(payload: dict, destination_url: str) -> dict:
    """
    Creates a tiny landing config (UTM + redirect) for stable funnel tracking.
    """
    return {
        "destination_url": destination_url,
        "bonus_link": payload.get("bonus_link",""),
        "coupon_code": payload.get("coupon_code",""),
        "segment": payload.get("segment",""),
        "platform": payload.get("platform",""),
    }

def write_json(path: Path, obj: dict):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

def write_landing_html(path: Path, destination_url: str):
    html = f"""<!doctype html><html><head><meta charset='utf-8'>
<meta http-equiv="refresh" content="0;url={destination_url}">
<title>AllokiDalloki Landing</title></head><body>
Redirecting... <a href="{destination_url}">continue</a>
</body></html>"""
    path.write_text(html, encoding="utf-8")

from urllib.parse import quote

def write_landing_html_variants(out_dir: Path, destination_url: str, coupon_code: str, variants: int = 2, track_url: str = "") -> list[Path]:
    """
    Generate landing_A/B/C.html with:
    - coupon copy button
    - tracking beacon to track_url (POST /event/visit or GET pixel) if provided
    Destination URL gets appended with ?utm_source=...&utm_campaign=...&v=A etc (best-effort).
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    letters = ["A","B","C"][:max(1, min(3, int(variants)))]
    files = []
    for v in letters:
        # simple param append
        sep = "&" if "?" in destination_url else "?"
        dest = f"{destination_url}{sep}utm_medium=profile_link&utm_campaign=seasonpack_landing&v={v}"
        # tracking: try sendBeacon; fallback image pixel
        track_js = ""
        track_img = ""
        if track_url:
            # if user provides base like https://example.com/event/visit
            track_js = f"""
<script>
(function(){{
  try {{
    var payload = {{variant: "{v}", ts: new Date().toISOString(), ua: navigator.userAgent}};
    if (navigator.sendBeacon) {{
      navigator.sendBeacon("{track_url}", new Blob([JSON.stringify(payload)], {{type:"application/json"}}));
    }} else {{
      fetch("{track_url}", {{method:"POST", headers:{{"Content-Type":"application/json"}}, body: JSON.stringify(payload)}});
    }}
  }} catch(e){{}}
}})();
</script>
"""
            # pixel GET fallback endpoint if accepts query
            track_img = f'<img src="{track_url}?variant={v}&t={quote("1")}" width="1" height="1" style="display:none" />'
        html = f"""<!doctype html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AllokiDalloki Landing {v}</title>
<style>
body{{font-family:system-ui,-apple-system,Segoe UI,Roboto; background:#fff; margin:0; padding:24px;}}
.card{{max-width:520px; margin:0 auto; border:1px solid #eee; border-radius:18px; padding:18px;}}
.badge{{display:inline-block; padding:6px 10px; border-radius:999px; background:#111; color:#fff; font-size:12px;}}
.btn{{display:block; width:100%; padding:14px 16px; border:0; border-radius:14px; font-size:16px; font-weight:700;}}
.primary{{background:#111; color:#fff;}}
.secondary{{background:#f2f2f2; color:#111; margin-top:10px;}}
.small{{font-size:12px; color:#666; margin-top:10px; line-height:1.5;}}
.code{{font-weight:800; letter-spacing:1px;}}
</style>
</head>
<body>
<div class="card">
  <div class="badge">SEASONPACK · Landing {v}</div>
  <h2 style="margin:12px 0 6px;">보너스 카드가 열렸어요 🐶🌈</h2>
  <div class="small">쿠폰코드: <span class="code" id="coupon">{coupon_code}</span></div>
  <button class="btn secondary" id="copyBtn">쿠폰 복사하기</button>
  <button class="btn primary" onclick="location.href='{dest}'">지금 구매하러 가기</button>
  <div class="small">* 이 페이지는 프로필 링크 전용 랜딩입니다. (변형 {v})</div>
</div>
<script>
document.getElementById('copyBtn').addEventListener('click', async function(){{
  var c = document.getElementById('coupon').innerText;
  try {{
    await navigator.clipboard.writeText(c);
    this.innerText = '복사 완료!';
    setTimeout(()=>this.innerText='쿠폰 복사하기', 1500);
  }} catch(e) {{
    // fallback
    var ta=document.createElement('textarea'); ta.value=c; document.body.appendChild(ta); ta.select();
    document.execCommand('copy'); ta.remove();
    this.innerText = '복사 완료!';
    setTimeout(()=>this.innerText='쿠폰 복사하기', 1500);
  }}
}});
</script>
{track_img}
{track_js}
</body></html>"""
        p = out_dir / f"landing_{v}.html"
        p.write_text(html, encoding="utf-8")
        files.append(p)
    return files
