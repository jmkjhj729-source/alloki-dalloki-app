from __future__ import annotations
from pathlib import Path

def render_landing_html(variant: str, destination_url: str, coupon_code: str) -> str:
    headline = {
        "A": "오늘만 혜택 열림 🎁",
        "B": "지금 가장 많이 선택돼요 🔥",
        "C": "시즌팩 VIP 혜택 💎",
    }.get(variant, "혜택 확인")

    sub = {
        "A": "보너스 카드 + 쿠폰 즉시 제공",
        "B": "마감 전 구매 급증 중",
        "C": "프리미엄 구매자 혜택 포함",
    }.get(variant, "")

    btn = {
        "A": "혜택 받고 이동",
        "B": "지금 바로 구매",
        "C": "VIP 혜택 보기",
    }.get(variant, "이동")

    return f"""<!doctype html>
<html lang='ko'><head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>AllokiDalloki Landing {variant}</title>
<style>
body{{font-family:system-ui,-apple-system;display:flex;align-items:center;justify-content:center;background:#fafafa}}
.card{{max-width:420px;background:#fff;border-radius:16px;padding:24px;box-shadow:0 10px 30px rgba(0,0,0,.08)}}
h1{{font-size:22px;margin:0 0 8px}}
p{{color:#555;margin:0 0 16px}}
.btn{{display:block;text-align:center;background:#ff6b6b;color:#fff;padding:14px;border-radius:12px;text-decoration:none;font-weight:700}}
.copy{{margin-top:12px;display:flex;gap:8px}}
.copy input{{flex:1;padding:10px;border-radius:8px;border:1px solid #ddd}}
.copy button{{padding:10px 14px;border-radius:8px;border:none;background:#333;color:#fff}}
.small{{margin-top:10px;font-size:12px;color:#777;text-align:center}}
</style>
<script>
function copyCoupon(){{
  const i=document.getElementById('coupon');
  i.select();i.setSelectionRange(0,99999);
  document.execCommand('copy');
  document.getElementById('copyst').innerText='복사됨!';
}}
</script>
</head>
<body>
<div class='card'>
  <h1>{headline}</h1>
  <p>{sub}</p>
  <a class='btn' href='{destination_url}'>{btn}</a>
  <div class='copy'>
    <input id='coupon' value='{coupon_code}' readonly>
    <button onclick='copyCoupon()'>쿠폰 복사</button>
  </div>
  <div id='copyst' class='small'>쿠폰을 눌러 복사하세요</div>
  <div class='small'>variant {variant}</div>
</div>
</body></html>"""
