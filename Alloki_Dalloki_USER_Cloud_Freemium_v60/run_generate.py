# run_generate.py
from __future__ import annotations

import os
import base64
import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

# ✅ 진짜 이미지 생성만: OpenAI Images API (gpt-image-1)
from openai import OpenAI  # requirements.txt에 openai 필요
from PIL import Image      # requirements.txt에 Pillow 필요
from io import BytesIO

MODEL = "gpt-image-1"
OUTPUT_FORMAT = "png"

# GPT Image 모델 size 허용값: 1024x1024 / 1024x1536 / 1536x1024 / auto :contentReference[oaicite:4]{index=4}
SIZE_SQUARE = "1024x1024"
SIZE_STORY = "1024x1536"

OUT_DIR = Path("outputs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_PROMPT = (
    "Two adorable pastel rainbow baby poodles, Alloki and Dalloki. "
    "Fluffy cotton-candy fur, big sparkling eyes, gentle smiles. "
    "Soft lighting, clean composition, storybook illustration style, high detail fur. "
    "Leave generous empty space for text overlay. "
    "No text, no letters, no watermark."
)

SEASON_ADDONS: Dict[str, str] = {
    "spring": "Soft peach and cream background, warm spring light, tender mood.",
    "summer": "Soft mint and ivory background, cool calm summer light.",
    "autumn": "Oatmeal and warm brown background, cozy reflective mood.",
    "winter": "Ivory and light gray-blue background, calm winter mood.",
}


@dataclass
class GenerateResult:
    ok: bool
    msg: str
    season: str
    offer_code: str
    plan_label: str
    copy: Dict[str, str]
    prompt: str
    image_path: Optional[str]


def _require_api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY가 없습니다. Streamlit Cloud → Settings → Secrets에 "
            'OPENAI_API_KEY="YOUR_KEY" 를 넣어야 합니다.'
        )
    return key


def offer_plan(offer_code: str, bonus_arg: int = 0):
    oc = (offer_code or "").strip().upper()
    if oc == "D7":
        return 7, 0, "7일"
    if oc == "D14":
        return 14, 0, "14일"
    if oc == "D21":
        return 21, 0, "21일"
    if oc == "SEASONPACK":
        bonus = bonus_arg if bonus_arg else 3
        return 21, bonus, "시즌팩"
    return 7, 0, "7일"


def thumb_copy_for_offer(offer_code: str, season: str) -> Dict[str, str]:
    oc = (offer_code or "").strip().upper()
    sk = (season or "spring").strip().lower()
    season_kr = {"spring": "봄", "summer": "여름", "autumn": "가을", "winter": "겨울"}.get(sk, "시즌")

    if oc == "SEASONPACK":
        return {
            "A": f"{season_kr} 시즌팩 21+3 · 오늘의 마음",
            "B": f"{season_kr} 시즌팩 21+3 · 지금 안 사면 늦어요",
            "C": f"{season_kr} 시즌팩 21+3 · 프리미엄 한정",
        }

    if oc == "D7":
        return {"A": "7일 카드 · 오늘의 마음", "B": "7일 카드 · 지금 시작", "C": "7일 카드 · 라이트"}
    if oc == "D14":
        return {"A": "14일 카드 · 마음 회복", "B": "14일 카드 · 놓치면 후회", "C": "14일 카드 · 프리미엄"}
    if oc == "D21":
        return {"A": "21일 카드 · 마음 루틴", "B": "21일 카드 · 지금이 타이밍", "C": "21일 카드 · 깊은 힐링"}

    return {"A": "오늘의 마음을 꺼내보세요", "B": "지금 안 보면 놓쳐요", "C": "프리미엄 감성"}


def build_prompt(season: str, mood: str = "calm") -> str:
    sk = (season or "spring").strip().lower()
    addon = SEASON_ADDONS.get(sk, "")
    mood_txt = f"Overall mood: {mood}. " if mood else ""
    return f"{BASE_PROMPT} {mood_txt}{addon}"


def _generate_image_bytes(prompt: str, size: str) -> bytes:
    _require_api_key()
    client = OpenAI()

    # Images API reference: output_format png/jpeg/webp, size 규칙 :contentReference[oaicite:5]{index=5}
    res = client.images.generate(
        model=MODEL,
        prompt=prompt,
        size=size,
        output_format=OUTPUT_FORMAT,
    )
    b64 = res.data[0].b64_json
    return base64.b64decode(b64)


def run_generate(
    *,
    user_name: str = "USER",
    offer_code: str = "D7",
    season: str = "spring",
    mood: str = "calm",
    size: str = SIZE_STORY,
) -> GenerateResult:
    user_name = (user_name or "USER").strip()
    offer_code = (offer_code or "D7").strip().upper()
    season = (season or "spring").strip().lower()

    days, bonus, label = offer_plan(offer_code=offer_code)
    copy = thumb_copy_for_offer(offer_code=offer_code, season=season)
    prompt = build_prompt(season=season, mood=mood)

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = OUT_DIR / f"{user_name}_{season}_{offer_code}_{stamp}.png"

    img_bytes = _generate_image_bytes(prompt=prompt, size=size)

    # 저장 & 파일 검사(진짜 이미지 생성됐는지)
    out_path.write_bytes(img_bytes)

    # PIL로 열어보기까지 성공해야 "진짜 이미지"로 판정
    _ = Image.open(BytesIO(img_bytes)).convert("RGBA")

    return GenerateResult(
        ok=True,
        msg=f"✅ 진짜 이미지 생성 성공! (플랜={label}, {days}일, bonus={bonus})",
        season=season,
        offer_code=offer_code,
        plan_label=label,
        copy=copy,
        prompt=prompt,
        image_path=str(out_path),
    )
