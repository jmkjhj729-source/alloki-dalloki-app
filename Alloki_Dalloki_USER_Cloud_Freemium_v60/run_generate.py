# run_generate.py
# v60: button click -> real actions
# - season pack branching
# - copy(text) generation
# - real image generation via OpenAI Images API (gpt-image-1)

from __future__ import annotations

import os
import base64
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Dict, Optional, Tuple

from PIL import Image
from openai import OpenAI


# -----------------------------
# Config
# -----------------------------
MODEL = "gpt-image-1"
SIZE_SQUARE = "1024x1024"
SIZE_STORY = "1024x1536"  # 세로(숏폼/스토리 느낌)

OUT_DIR = Path("outputs_v60")
OUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_PROMPT = (
    "Two adorable pastel rainbow baby poodles, Alloki and Dalloki. "
    "They are fluffy and cute, with big sparkling eyes, gentle expressions. "
    "Soft lighting, clean composition, storybook illustration style, high detail fur. "
    "No text, no letters, no watermark. "
)

SEASON_ADDONS: Dict[str, str] = {
    "spring": "Soft peach and cream background, warm spring light, fresh and tender mood.",
    "summer": "Soft mint and ivory background, cool calm mood, gentle summer light.",
    "autumn": "Oatmeal and warm brown background, cozy reflective mood, soft golden light.",
    "winter": "Ivory and light gray-blue background, calm winter mood, soft cool light.",
    "yearend_bundle": "Four-season subtle gradient ring feeling, premium calm mood, gift-like atmosphere.",
}

# 기본 문구(일반 상품)
THUMB_COPY_DEFAULT: Dict[str, str] = {
    "A": "오늘의 마음을 꺼내보세요",
    "B": "지금 안 보면 놓쳐요",
    "C": "사계절을 건너온 마음",
}


# -----------------------------
# Helpers
# -----------------------------
def _get_api_key() -> str:
    """
    Streamlit Cloud에서는 보통 Secrets에 넣지만,
    여기서는 환경변수 OPENAI_API_KEY를 기본으로 사용.
    """
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY가 비어있어요. Streamlit Cloud → Settings → Secrets 에 "
            "OPENAI_API_KEY를 설정하거나, 환경변수로 넣어주세요."
        )
    return key


def _openai_client() -> OpenAI:
    # openai 라이브러리는 환경변수 OPENAI_API_KEY를 자동 사용 가능하지만,
    # 확실하게 하기 위해 setdefault로 넣어줌
    os.environ.setdefault("OPENAI_API_KEY", _get_api_key())
    return OpenAI()


def _save_image_bytes(image_bytes: bytes, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(image_bytes)


def _image_bytes_to_pil(image_bytes: bytes) -> Image.Image:
    return Image.open(BytesIO(image_bytes)).convert("RGBA")


def _generate_image_bytes(
    client: OpenAI,
    prompt: str,
    size: str = SIZE_SQUARE,
    output_format: str = "png",
) -> bytes:
    """
    OpenAI Images API로 실제 이미지 생성.
    공식 예시: client.images.generate(model="gpt-image-1", prompt=..., size="1024x1024") :contentReference[oaicite:1]{index=1}
    """
    result = client.images.generate(
        model=MODEL,
        prompt=prompt,
        size=size,
        output_format=output_format,
    )
    b64 = result.data[0].b64_json
    return base64.b64decode(b64)


# -----------------------------
# Business Logic (Offer / Copy)
# -----------------------------
@dataclass
class OfferPlan:
    days: int
    bonus: int
    label: str


def offer_plan(offer_code: str, bonus_arg: int = 0) -> OfferPlan:
    """
    offer_code:
      - D7 / D14 / D21 : 고정 기간
      - SEASONPACK     : 시즌팩(21일 + 보너스 기본 3일)
      - 기타           : 커스텀(여기서는 기본값으로 처리)
    """
    oc = (offer_code or "").strip().upper()

    if oc == "D7":
        return OfferPlan(days=7, bonus=0, label="7일")
    if oc == "D14":
        return OfferPlan(days=14, bonus=0, label="14일")
    if oc == "D21":
        return OfferPlan(days=21, bonus=0, label="21일")
    if oc == "SEASONPACK":
        bonus = bonus_arg if bonus_arg else 3
        return OfferPlan(days=21, bonus=bonus, label="시즌팩")

    # fallback
    return OfferPlan(days=21, bonus=0, label="custom")


def thumb_copy_for_offer(offer_code: str, season: str) -> Dict[str, str]:
    """
    버튼 클릭 시 “문구 생성/분기”가 여기서 결정됨.
    - SEASONPACK이면 시즌명 포함 문구로 자동 변환
    - 그 외는 기본 문구 사용
    """
    oc = (offer_code or "").strip().upper()
    season_key = (season or "").strip().lower()

    if oc == "SEASONPACK":
        season_kr = {
            "spring": "봄",
            "summer": "여름",
            "autumn": "가을",
            "winter": "겨울",
            "yearend_bundle": "연말",
        }.get(season_key, "시즌")

        # ✅ f-string 따옴표/쉼표/괄호 오류 안 나게 “한 줄 문자열”로 안전하게 작성
        return {
            "A": f"{season_kr} 시즌팩 21+3 · 오늘의 마음을 꺼내요",
            "B": f"{season_kr} 시즌팩 21+3 · 지금 안 사면 늦어요",
            "C": f"{season_kr} 시즌팩 21+3 · 프리미엄 한정",
        }

    return dict(THUMB_COPY_DEFAULT)


def build_prompt(season: str, mood: str = "calm") -> str:
    """
    이미지 프롬프트는 BASE + 시즌 추가문구로 구성
    """
    season_key = (season or "").strip().lower()
    addon = SEASON_ADDONS.get(season_key, "")
    mood_txt = f"Overall mood: {mood}. " if mood else ""
    return BASE_PROMPT + mood_txt + addon


# -----------------------------
# Main entrypoint for Streamlit button
# -----------------------------
@dataclass
class GenerateResult:
    prompt: str
    offer: OfferPlan
    copy: Dict[str, str]
    image_path: Path


def run_generate(
    *,
    offer_code: str = "SEASONPACK",
    season: str = "spring",
    mood: str = "calm",
    out_name: str = "alloki_dalloki.png",
    size: str = SIZE_SQUARE,
) -> GenerateResult:
    """
    ✅ Streamlit 버튼 클릭 시 이 함수만 호출하면 됨.
    """
    client = _openai_client()

    offer = offer_plan(offer_code=offer_code)
    copy = thumb_copy_for_offer(offer_code=offer_code, season=season)

    prompt = build_prompt(season=season, mood=mood)
    img_bytes = _generate_image_bytes(client, prompt=prompt, size=size, output_format="png")

    out_path = OUT_DIR / out_name
    _save_image_bytes(img_bytes, out_path)

    return GenerateResult(
        prompt=prompt,
        offer=offer,
        copy=copy,
        image_path=out_path,
    )


# -----------------------------
# Optional: CLI test
# -----------------------------
if __name__ == "__main__":
    # 로컬에서 테스트할 때:
    # export OPENAI_API_KEY="..."
    res = run_generate(
        offer_code="SEASONPACK",
        season="spring",
        mood="calm",
        out_name="test_v60.png",
        size=SIZE_SQUARE,
    )
    print("OK:", res.image_path)
    print("PROMPT:", res.prompt)
    print("COPY:", res.copy)
