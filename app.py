# app.py
from __future__ import annotations

import base64
import io
import os
import random
import tempfile
from dataclasses import dataclass
from datetime import datetime

import numpy as np
import requests
import streamlit as st
from PIL import Image

try:
    import imageio.v2 as imageio  # requirements.txt에 imageio, imageio-ffmpeg 있음
except Exception:
    imageio = None


# =========================
# 0) 기본 설정
# =========================
st.set_page_config(page_title="알록이 & 달록이 앱", page_icon="🐼", layout="centered")

APP_TITLE = "알록이 & 달록이 앱"
MODEL_IMAGE = "gpt-image-1"
IMAGE_SIZE = "1024x1024"  # OpenAI Images API 지원 사이즈
FREE_LIMIT_PER_SESSION = 3  # 무료: 세션당 3회 (프리미엄은 무제한)

# Streamlit Secrets 우선, 없으면 환경변수
OPENAI_API_KEY = None
if hasattr(st, "secrets"):
    OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", None)
if not OPENAI_API_KEY:
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

PREMIUM_CODE = None
if hasattr(st, "secrets"):
    PREMIUM_CODE = st.secrets.get("PREMIUM_CODE", None)
if PREMIUM_CODE is None:
    PREMIUM_CODE = os.environ.get("PREMIUM_CODE", "")  # 선택(없어도 됨)


# =========================
# 1) 유틸 / 상태
# =========================
def init_state():
    st.session_state.setdefault("is_premium", False)
    st.session_state.setdefault("free_used", 0)
    st.session_state.setdefault("last_image_png", None)  # bytes
    st.session_state.setdefault("last_image_pil", None)  # PIL
    st.session_state.setdefault("last_copy", None)       # dict A/B/C
    st.session_state.setdefault("last_meta", None)       # dict


init_state()


def require_key_or_stop():
    if not OPENAI_API_KEY:
        st.error("OPENAI_API_KEY가 설정되어 있지 않아요. Streamlit Secrets에 OPENAI_API_KEY를 넣어주세요.")
        st.stop()


def is_allowed_generation() -> bool:
    if st.session_state["is_premium"]:
        return True
    return st.session_state["free_used"] < FREE_LIMIT_PER_SESSION


def consume_generation():
    if not st.session_state["is_premium"]:
        st.session_state["free_used"] += 1


# =========================
# 2) 시즌/오퍼 분기
# =========================
@dataclass
class Offer:
    code: str  # D7 / D14 / D21 / SEASONPACK
    days: int
    bonus: int
    label: str


def offer_plan(offer_code: str, season: str, bonus_arg: int | None = None) -> Offer:
    oc = (offer_code or "").upper().strip()
    if oc == "D7":
        return Offer(code="D7", days=7, bonus=0, label="7일 카드")
    if oc == "D14":
        return Offer(code="D14", days=14, bonus=0, label="14일 카드")
    if oc == "D21":
        return Offer(code="D21", days=21, bonus=0, label="21일 카드")
    # 기본: 시즌팩
    b = bonus_arg if (bonus_arg is not None) else 3
    return Offer(code="SEASONPACK", days=21, bonus=b, label="시즌팩")


def season_kr(season: str) -> str:
    return {
        "spring": "봄",
        "summer": "여름",
        "autumn": "가을",
        "winter": "겨울",
        "yearend_bundle": "연말",
    }.get(season, season)


# =========================
# 3) 캐릭터/스타일 분기 (프롬프트)
# =========================
def character_profile(character: str) -> dict:
    # 알록이/달록이 성격/포인트만 살짝 다르게
    if character == "달록이":
        return {
            "name": "Dalloki",
            "vibe": "playful, energetic, extrovert-like warmth",
            "pose": "slightly leaning forward, eager expression, lively tail",
            "accent": "a tiny star-shaped charm on collar",
        }
    # default 알록이
    return {
        "name": "Alloki",
        "vibe": "gentle, calm, introvert-like softness",
        "pose": "relaxed posture, cozy expression, calm tail",
        "accent": "a tiny heart-shaped charm on collar",
    }


SEASON_ADDONS = {
    "spring": "Soft peach & cream background, spring sunlight, warm bokeh sparkles.",
    "summer": "Soft mint & ivory background, cool calm mood, gentle sun rays.",
    "autumn": "Oatmeal & warm brown background, cozy reflective mood, soft grain.",
    "winter": "Ivory & light gray-blue background, soft winter light, subtle glitter.",
    "yearend_bundle": "Four-season subtle gradient ring background, premium calm feeling, tiny sparkles.",
}


def build_image_prompt(character: str, season: str, mood: str, offer: Offer) -> str:
    prof = character_profile(character)

    # “진짜 이미지 생성”용 프롬프트: 한 장 완결 / 깨끗한 배경 / 귀여움 / 고해상도
    # 알록이/달록이 스타일 분기: vibe/pose/accent가 다름
    prompt = f"""
A single, high-resolution, heart-melting illustration of TWO adorable pastel rainbow baby poodles sitting together.
Character focus: {prof["name"]} style variation, {prof["vibe"]}. Pose detail: {prof["pose"]}. Accessory: {prof["accent"]}.
Both puppies have big round sparkling eyes (eyes fully open), short muzzles, tiny tongues, extremely fluffy cotton-candy fur.
Composition: centered, clean, minimal background, cozy and cute, storybook style, soft lighting, detailed fur texture.
Season vibe: {SEASON_ADDONS.get(season, "")}
Mood keyword: {mood}.
No text, no letters, no watermark, no logo.
""".strip()

    # 오퍼에 따라 살짝 분위기 강화(무료/유료 느낌 분기)
    if offer.code == "SEASONPACK":
        prompt += "\nAdd a premium polish: slightly richer lighting, cleaner composition, extra subtle sparkles."

    return prompt


# =========================
# 4) 문구(A/B/C) 생성 (템플릿 기반)
# =========================
def generate_copy(character: str, season: str, offer: Offer) -> dict:
    sk = season_kr(season)
    name = "알록이" if character == "알록이" else "달록이"

    # A=공감형 / B=긴급형 / C=프리미엄형 (사용자 요구 반영)
    A_pool = [
        f"{sk}의 마음, {name}랑 꺼내볼래?",
        f"오늘 마음이 조금 무거웠지… {name}가 옆에 있어.",
        f"괜찮아. {name}랑 천천히 해도 돼.",
    ]
    B_pool = [
        f"지금 안 하면 놓쳐요! ({offer.label})",
        f"오늘이 제일 좋아요—지금 시작!",
        f"딱 지금이 타이밍! {offer.label}",
    ]
    C_pool = [
        f"{sk} 시즌팩 {offer.days}+{offer.bonus} (프리미엄 감성)",
        f"{sk} 한정—부드럽게 업그레이드",
        f"프리미엄 무드로 딱 정리해드려요",
    ]

    # 오퍼가 D7/D14/D21이면 B 문구에 좀 더 맞춰줌
    if offer.code in ("D7", "D14", "D21"):
        B_pool = [
            f"{offer.label} — 지금 시작하면 딱 좋아요!",
            f"{offer.label} — 놓치면 후회!",
            f"{offer.label} — 오늘부터 가볍게!",
        ]

    return {
        "A": random.choice(A_pool),
        "B": random.choice(B_pool),
        "C": random.choice(C_pool),
    }


# =========================
# 5) OpenAI "진짜 이미지 생성" (gpt-image-1)
# =========================
def openai_generate_image(prompt: str, size: str = IMAGE_SIZE) -> bytes:
    """
    OpenAI Images API (gpt-image-1) 호출 → PNG bytes 반환
    """
    require_key_or_stop()

    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL_IMAGE,
        "prompt": prompt,
        "size": size,
        # 필요하면 여기서 quality/style 등을 추가할 수 있음
    }

    r = requests.post(url, headers=headers, json=payload, timeout=120)
    if r.status_code != 200:
        # 에러 메시지를 최대한 보여주기
        try:
            msg = r.json()
        except Exception:
            msg = r.text
        raise RuntimeError(f"이미지 생성 실패: {r.status_code}\n{msg}")

    data = r.json()
    b64 = data["data"][0]["b64_json"]
    return base64.b64decode(b64)


# =========================
# 6) "진짜 영상 생성" (이미지 → mp4)
#    - 이미지 한 장으로 5초짜리 Ken Burns(줌) 영상 생성
# =========================
def make_video_mp4_from_image(png_bytes: bytes, seconds: int = 5, fps: int = 24) -> bytes:
    if imageio is None:
        raise RuntimeError("imageio가 설치되어 있지 않습니다. requirements.txt에 imageio, imageio-ffmpeg가 필요해요.")

    img = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    w, h = img.size

    total_frames = max(1, seconds * fps)

    # 줌 인 효과 (1.00 -> 1.08)
    start_zoom = 1.00
    end_zoom = 1.08

    frames = []
    for i in range(total_frames):
        t = i / (total_frames - 1) if total_frames > 1 else 0.0
        z = start_zoom + (end_zoom - start_zoom) * t

        nw, nh = int(w * z), int(h * z)
        resized = img.resize((nw, nh), Image.LANCZOS)

        # 가운데 크롭해서 원본 크기로
        left = (nw - w) // 2
        top = (nh - h) // 2
        cropped = resized.crop((left, top, left + w, top + h))
        frames.append(np.array(cropped))

    # mp4 임시파일로 저장 후 bytes로 읽기
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tf:
        tmp_path = tf.name

    try:
        writer = imageio.get_writer(tmp_path, fps=fps, codec="libx264", quality=8)
        for fr in frames:
            writer.append_data(fr)
        writer.close()

        with open(tmp_path, "rb") as f:
            return f.read()
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass


# =========================
# 7) UI
# =========================
st.markdown(f"## 🐼 {APP_TITLE}")
st.caption("Streamlit 배포 성공 ✨")

with st.sidebar:
    st.subheader("⚙️ 설정")

    season = st.selectbox(
        "시즌 선택",
        ["spring", "summer", "autumn", "winter", "yearend_bundle"],
        format_func=lambda x: {
            "spring": "봄",
            "summer": "여름",
            "autumn": "가을",
            "winter": "겨울",
            "yearend_bundle": "연말 번들",
        }.get(x, x),
        index=3,
    )

    mood = st.selectbox(
        "무드(분위기)",
        ["따뜻함", "설렘", "힐링", "귀여움 폭발", "조용한 행복"],
        index=0,
    )

    offer_code = st.selectbox(
        "상품/분기(테스트용)",
        ["SEASONPACK", "D7", "D14", "D21"],
        index=0,
        help="시즌팩/7일/14일/21일 분기를 테스트할 수 있어요.",
    )

    bonus_arg = None
    if offer_code == "SEASONPACK":
        bonus_arg = st.slider("시즌팩 보너스(기본 3)", min_value=0, max_value=10, value=3)

    st.divider()
    st.subheader("🧠 무료 / 유료 제한")

    if st.session_state["is_premium"]:
        st.success("프리미엄 활성화됨 ✅ (무제한)")
    else:
        remain = max(0, FREE_LIMIT_PER_SESSION - st.session_state["free_used"])
        st.info(f"무료 남은 횟수(세션 기준): {remain} / {FREE_LIMIT_PER_SESSION}")

    if PREMIUM_CODE:
        code_in = st.text_input("프리미엄 코드(있을 때만)", type="password")
        if code_in and code_in == PREMIUM_CODE:
            st.session_state["is_premium"] = True
            st.success("프리미엄 잠금 해제 완료 ✅")
    else:
        st.caption("※ PREMIUM_CODE가 설정되어 있지 않으면 프리미엄 잠금 기능은 숨겨진 상태로 동작해요.")

st.markdown("이제 여기에 UI를 하나씩 붙이면 됩니다.")

col1, col2 = st.columns(2)

# =========================
# 8) 버튼 클릭 → 실제 동작 연결 (알록이/달록이)
# =========================
def run_flow(character: str):
    if not is_allowed_generation():
        st.error("무료 사용 횟수를 다 썼어요 😭 프리미엄을 활성화하거나 새 세션에서 다시 시도해 주세요.")
        return

    offer = offer_plan(offer_code, season, bonus_arg)
    prompt = build_image_prompt(character, season, mood, offer)
    copy = generate_copy(character, season, offer)

    with st.spinner("진짜 이미지 생성 중... (OpenAI)"):
        png = openai_generate_image(prompt, size=IMAGE_SIZE)

    pil = Image.open(io.BytesIO(png)).convert("RGBA")

    st.session_state["last_image_png"] = png
    st.session_state["last_image_pil"] = pil
    st.session_state["last_copy"] = copy
    st.session_state["last_meta"] = {
        "character": character,
        "season": season,
        "mood": mood,
        "offer": offer.__dict__,
        "prompt": prompt,
        "time": datetime.now().isoformat(timespec="seconds"),
    }

    consume_generation()

    st.success(f"{character} 생성 완료 ✅")
    st.image(pil, use_container_width=True)

    st.markdown("### ✍️ 문구 (A/B/C)")
    st.write(f"**A (공감형):** {copy['A']}")
    st.write(f"**B (긴급형):** {copy['B']}")
    st.write(f"**C (프리미엄형):** {copy['C']}")

    # 다운로드
    st.download_button(
        "⬇️ 이미지 다운로드 (PNG)",
        data=png,
        file_name=f"{character}_{season}_{offer.code}.png",
        mime="image/png",
        use_container_width=True,
    )


with col1:
    if st.button("🐼 알록이 시작하기", use_container_width=True):
        try:
            run_flow("알록이")
        except Exception as e:
            st.exception(e)

with col2:
    if st.button("🐼 달록이 시작하기", use_container_width=True):
        try:
            run_flow("달록이")
        except Exception as e:
            st.exception(e)


# =========================
# 9) 🎬 영상 생성 연결 (이미지 생성 후)
# =========================
st.markdown("---")
st.markdown("## 🎬 영상 생성")

if st.session_state["last_image_png"] is None:
    st.info("먼저 알록이/달록이 이미지를 한 번 생성해 주세요.")
else:
    vcol1, vcol2 = st.columns([1, 1])

    with vcol1:
        seconds = st.slider("영상 길이(초)", 2, 10, 5)
    with vcol2:
        fps = st.selectbox("FPS", [12, 24, 30], index=1)

    st.caption("※ ‘진짜 영상 생성’입니다: 생성된 이미지를 기반으로 MP4 파일을 만들어 다운로드합니다.")

    if st.button("🎬 MP4 만들기 (줌 효과)", use_container_width=True):
        try:
            with st.spinner("영상 렌더링 중..."):
                mp4_bytes = make_video_mp4_from_image(st.session_state["last_image_png"], seconds=seconds, fps=fps)

            st.success("영상 생성 완료 ✅")
            st.video(mp4_bytes)

            meta = st.session_state.get("last_meta") or {}
            character = meta.get("character", "poodle")
            season = meta.get("season", "season")
            st.download_button(
                "⬇️ 영상 다운로드 (MP4)",
                data=mp4_bytes,
                file_name=f"{character}_{season}_{seconds}s.mp4",
                mime="video/mp4",
                use_container_width=True,
            )
        except Exception as e:
            st.exception(e)


# =========================
# 10) 디버그(원하면 펼쳐보기)
# =========================
with st.expander("🧾 디버그 정보(프롬프트/분기 확인)"):
    st.json(st.session_state.get("last_meta", {}))
