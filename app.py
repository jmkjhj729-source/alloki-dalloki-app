# app.py
import os
import base64
from datetime import datetime
import requests
import streamlit as st

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(page_title="알록이 & 달록이 앱", page_icon="🐼", layout="centered")

MODEL = "gpt-image-1"          # 이미지 모델
IMAGE_SIZE = "1024x1024"       # OpenAI 이미지 생성 size
TIMEOUT_SEC = 120

# 알록이/달록이 기본 프롬프트 (원하면 여기 문장만 수정)
BASE_PROMPT_LINES = [
    "Two adorable pastel rainbow baby poodles, Alloki and Dalloki.",
    "Sitting calmly side by side, gentle expressions, minimal background.",
    "Ivory tone, clean composition, emotional but quiet mood, storybook style, high resolution.",
    "Leave generous empty space for text overlay.",
    "No text, no letters, no watermark."
]

SEASON_ADDONS = {
    "spring":  "Soft peach and cream background, spring light.",
    "summer":  "Soft mint and ivory background, cool calm mood.",
    "autumn":  "Oatmeal and warm brown background, reflective mood.",
    "winter":  "Ivory and light gray-blue background, soft winter light.",
    "yearend_bundle": "Four-season subtle gradient ring, premium calm feeling.",
}

THUMB_COPY_DEFAULT = {
    "A": "오늘의 마음을 꺼내보세요.",
    "B": "지금 안 보면 놓쳐요.",
    "C": "사계절을 건너온 마음.",
}

# -----------------------------
# 유틸: API KEY 읽기
# -----------------------------
def get_api_key() -> str:
    # 1) Streamlit secrets 우선
    if "OPENAI_API_KEY" in st.secrets:
        return str(st.secrets["OPENAI_API_KEY"]).strip()
    # 2) 환경변수
    return os.environ.get("OPENAI_API_KEY", "").strip()

# -----------------------------
# 유틸: OpenAI "진짜 이미지 생성" (requests로 직접 호출)
# -----------------------------
def openai_generate_image(prompt: str, size: str = IMAGE_SIZE) -> bytes:
    api_key = get_api_key()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY가 없습니다. Streamlit Secrets 또는 환경변수에 설정하세요.")

    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "size": size,
    }

    r = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT_SEC)
    if r.status_code != 200:
        # 에러 메시지 최대한 보기 쉽게
        try:
            detail = r.json()
        except Exception:
            detail = r.text
        raise RuntimeError(f"이미지 생성 실패 (HTTP {r.status_code}): {detail}")

    data = r.json()
    # 일반적으로 b64_json 형태로 옴
    b64 = data["data"][0].get("b64_json")
    if not b64:
        raise RuntimeError(f"이미지 응답에 b64_json이 없습니다: {data}")

    return base64.b64decode(b64)

# -----------------------------
# 시즌팩/기간팩 문구 분기
# -----------------------------
def pick_copy(offer_code: str, season_key: str) -> dict:
    oc = (offer_code or "").upper().strip()

    # 시즌팩이면 시즌명 붙인 문구로 변경
    if oc == "SEASONPACK":
        season_kr = {
            "spring": "봄",
            "summer": "여름",
            "autumn": "가을",
            "winter": "겨울",
            "yearend_bundle": "연말",
        }.get(season_key, "시즌")

        return {
            "A": f"{season_kr} 시즌팩 21+3 · 오늘의 마음을 꺼내요",
            "B": f"{season_kr} 시즌팩 21+3 · 지금 안 사면 늦어요",
            "C": f"{season_kr} 시즌팩 21+3 · 프리미엄 한정",
        }

    # 기간팩(예: 7일/14일/21일)
    if oc == "D7":
        return {"A": "7일 카드 · 오늘의 마음", "B": "7일 카드 · 지금 시작", "C": "7일 카드 · 가볍게 힐링"}
    if oc == "D14":
        return {"A": "14일 카드 · 마음 회복", "B": "14일 카드 · 놓치면 후회", "C": "14일 카드 · 더 깊게"}
    if oc == "D21":
        return {"A": "21일 카드 · 마음 루틴", "B": "21일 카드 · 지금이 타이밍", "C": "21일 카드 · 프리미엄 감성"}

    # 기본
    return THUMB_COPY_DEFAULT.copy()

# -----------------------------
# 프롬프트 조합
# -----------------------------
def build_prompt(season_key: str, extra_text: str) -> str:
    lines = list(BASE_PROMPT_LINES)
    if season_key in SEASON_ADDONS:
        lines.append(SEASON_ADDONS[season_key])
    if extra_text and extra_text.strip():
        lines.append(extra_text.strip())
    return "\n".join(lines)

# -----------------------------
# UI
# -----------------------------
st.markdown("## 🐼 알록이 & 달록이 앱")
st.caption("Streamlit 배포 성공 ✅  이제 버튼 클릭 시 ‘진짜 이미지 생성’까지 연결합니다.")

with st.sidebar:
    st.markdown("### 설정")
    season_key = st.selectbox(
        "시즌 선택",
        options=["spring", "summer", "autumn", "winter", "yearend_bundle"],
        format_func=lambda x: {
            "spring":"봄(spring)",
            "summer":"여름(summer)",
            "autumn":"가을(autumn)",
            "winter":"겨울(winter)",
            "yearend_bundle":"연말 번들(yearend_bundle)"
        }.get(x, x),
        index=0
    )

    offer_code = st.selectbox(
        "상품/분기(시즌팩/기간팩)",
        options=["", "SEASONPACK", "D7", "D14", "D21"],
        format_func=lambda x: {
            "":"(기본)",
            "SEASONPACK":"SEASONPACK (시즌팩 21+3)",
            "D7":"D7 (7일)",
            "D14":"D14 (14일)",
            "D21":"D21 (21일)"
        }.get(x, x),
        index=0
    )

    extra_text = st.text_area(
        "추가 요청(선택)",
        placeholder="예) cozy living room, soft bokeh sparkles, ultra fluffy fur, disney-like illustration",
        height=120
    )

st.markdown("### 1️⃣ 버튼 클릭 → 실제 동작 연결")
st.write("**알록이 시작하기**를 누르면 👉 이미지 생성 + 문구 생성 + 시즌팩 분기 결과를 바로 보여줍니다.")

btn = st.button("🐶 알록이 시작하기", use_container_width=True)

if btn:
    try:
        with st.status("v60 실행중… 진짜 이미지 생성하는 중 🧸", expanded=True) as status:
            prompt = build_prompt(season_key, extra_text)
            st.code(prompt, language="text")

            img_bytes = openai_generate_image(prompt, size=IMAGE_SIZE)
            copy_dict = pick_copy(offer_code, season_key)

            status.update(label="✅ 생성 완료!", state="complete", expanded=False)

        st.success("✅ v60 연결 성공! (진짜 이미지 생성 완료)")

        st.markdown("### 🖼️ 생성된 이미지")
        st.image(img_bytes, use_container_width=True)

        st.markdown("### 📝 문구(A/B/C)")
        col1, col2, col3 = st.columns(3)
        col1.write(f"**A**: {copy_dict['A']}")
        col2.write(f"**B**: {copy_dict['B']}")
        col3.write(f"**C**: {copy_dict['C']}")

        # 다운로드
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label="⬇️ 이미지 다운로드(PNG)",
            data=img_bytes,
            file_name=f"alloki_dalloki_{season_key}_{ts}.png",
            mime="image/png",
            use_container_width=True,
        )

    except Exception as e:
        st.error(f"❌ 실행 실패: {e}")

# 도움말/체크
st.markdown("---")
st.markdown("### ✅ 체크리스트")
st.write("- Streamlit Secrets에 `OPENAI_API_KEY`가 들어있나요?")
st.write("- 버튼 누르면 아래에 **이미지 + 문구**가 바로 뜨나요?")
st.write("- 시즌을 바꾸면 분위기/문구가 바뀌나요?")
