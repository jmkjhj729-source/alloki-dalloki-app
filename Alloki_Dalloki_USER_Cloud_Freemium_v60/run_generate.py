# run_generate.py
# ------------------------------------------------------------
# Alloki & Dalloki - Clean, Safe, No-indentation-error version
# 버튼 클릭 -> 문구 생성 -> 시즌팩 분기 -> (샘플) 이미지 생성
# ------------------------------------------------------------

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple
import datetime

# -----------------------------
# 기본 설정
# -----------------------------
OUT_SQUARE: Tuple[int, int] = (1080, 1080)
OUT_STORY: Tuple[int, int] = (1080, 1920)

BASE_PROMPT: str = (
    "Two adorable pastel rainbow baby poodles, Alloki and Dalloki. "
    "Sitting calmly side by side, gentle expressions, minimal background. "
    "Ivory tone, clean composition, emotional but quiet mood, storybook style. "
    "Leave generous empty space for text overlay. No text, no letters, no watermark."
)

SEASON_ADDONS: Dict[str, str] = {
    "spring": "Soft peach and cream background, spring light.",
    "summer": "Soft mint and ivory background, cool calm mood.",
    "autumn": "Oatmeal and warm brown background, reflective mood.",
    "winter": "Ivory and light gray-blue background, soft winter light.",
    "yearend_bundle": "Four-season subtle gradient ring, premium calm feeling.",
}

# -----------------------------
# 결과 타입
# -----------------------------
@dataclass
class RunResult:
    ok: bool
    msg: str
    user_name: str
    season: str
    offer_code: str
    plan_label: str
    copy: Dict[str, str]              # {"A": "...", "B": "...", "C": "..."}
    image_path: Optional[str]         # 생성된 이미지 경로(샘플)
    created_at: str


# -----------------------------
# 1) 플랜/시즌팩 분기
# -----------------------------
def offer_plan(offer_code: str, season: str) -> Tuple[int, int, str]:
    """
    returns: (days, bonus, label)
    """
    oc = (offer_code or "").upper().strip()

    if oc == "D7":
        return 7, 0, "7일 카드"
    if oc == "D14":
        return 14, 0, "14일 카드"
    if oc == "D21":
        return 21, 0, "21일 카드"
    if oc == "SEASONPACK":
        # 시즌팩은 21+3 같은 느낌
        return 21, 3, f"{season} 시즌팩"
    # default
    return 7, 0, "7일 카드"


# -----------------------------
# 2) 문구 생성 (A/B/C)
# -----------------------------
def thumb_copy_for_offer(offer_code: str, season: str) -> Dict[str, str]:
    oc = (offer_code or "").upper().strip()
    sk = (season or "spring").lower().strip()
    season_kr = {"spring": "봄", "summer": "여름", "autumn": "가을", "winter": "겨울"}.get(sk, "시즌")

    # 기본 문구(일반)
    if oc in ("D7", "D14", "D21"):
        if oc == "D7":
            days = "7일"
        elif oc == "D14":
            days = "14일"
        else:
            days = "21일"

        return {
            "A": f"{days} 카드 · 오늘의 마음",
            "B": f"{days} 카드 · 지금 시작",
            "C": f"{days} 카드 · 프리미엄",
        }

    # 시즌팩 문구
    if oc == "SEASONPACK":
        return {
            "A": f"{season_kr} 시즌팩 21+3 · 오늘의 마음",
            "B": f"{season_kr} 시즌팩 21+3 · 지금 안 사면 늦어요",
            "C": f"{season_kr} 시즌팩 21+3 · 프리미엄 한정",
        }

    # fallback
    return {
        "A": "오늘의 마음을 꺼내보세요",
        "B": "지금 안 보면 놓쳐요",
        "C": "사계절을 건너온 마음",
    }


# -----------------------------
# 3) 프롬프트 만들기
# -----------------------------
def build_prompt(user_name: str, season: str, plan_label: str) -> str:
    sk = (season or "spring").lower().strip()
    addon = SEASON_ADDONS.get(sk, "")
    return (
        f"{BASE_PROMPT}\n"
        f"Season addon: {addon}\n"
        f"User: {user_name}\n"
        f"Plan: {plan_label}\n"
        f"Make one cohesive heartwarming scene."
    )


# -----------------------------
# 4) (샘플) 이미지 생성 - 항상 성공하는 안전 버전
#    -> PIL이 없으면 텍스트 파일로라도 결과를 남김
# -----------------------------
def generate_placeholder_image(out_path: Path, text: str, size: Tuple[int, int]) -> None:
    try:
        from PIL import Image, ImageDraw

        img = Image.new("RGB", size, (245, 245, 245))
        draw = ImageDraw.Draw(img)
        draw.text((40, 40), "Alloki & Dalloki (placeholder)", fill=(30, 30, 30))
        draw.text((40, 90), text[:500], fill=(50, 50, 50))
        img.save(out_path)
    except Exception:
        # PIL이 없거나 에러면 txt로라도 저장
        out_path.with_suffix(".txt").write_text(text, encoding="utf-8")


# -----------------------------
# 버튼이 호출할 "단 하나"의 함수
# -----------------------------
def run_all(
    user_name: str,
    season: str = "spring",
    offer_code: str = "D7",
    out_dir: str = "outputs",
) -> RunResult:
    user_name = (user_name or "").strip() or "USER"
    season = (season or "spring").strip().lower()
    offer_code = (offer_code or "D7").strip().upper()

    # 1) 폴더 준비
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    try:
        # 2) 시즌팩/플랜 분기
        days, bonus, plan_label = offer_plan(offer_code=offer_code, season=season)

        # 3) 문구 생성
        copy = thumb_copy_for_offer(offer_code=offer_code, season=season)

        # 4) 이미지 생성(샘플)
        prompt = build_prompt(user_name=user_name, season=season, plan_label=plan_label)

        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        img_path = out / f"{user_name}_{season}_{offer_code}_{stamp}.png"

        # 스토리형 세로 이미지로 샘플 생성
        generate_placeholder_image(out_path=img_path, text=prompt, size=OUT_STORY)

        return RunResult(
            ok=True,
            msg=f"성공! (플랜={plan_label}, days={days}, bonus={bonus})",
            user_name=user_name,
            season=season,
            offer_code=offer_code,
            plan_label=plan_label,
            copy=copy,
            image_path=str(img_path) if img_path.exists() else None,
            created_at=stamp,
        )

    except Exception as e:
        return RunResult(
            ok=False,
            msg=f"오류: {e}",
            user_name=user_name,
            season=season,
            offer_code=offer_code,
            plan_label="unknown",
            copy={},
            image_path=None,
            created_at=datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
        )
