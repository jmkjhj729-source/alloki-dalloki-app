import os
import time
import streamlit as st

st.set_page_config(page_title="알록이 & 달록이 앱", page_icon="🐼", layout="centered")

# ---------------------------
# 간단 유틸
# ---------------------------
def is_paid_user() -> bool:
    # Streamlit secrets에 PLAN="paid" 넣으면 유료로 동작
    # 무료면 기본값 "free"
    plan = st.secrets.get("PLAN", os.environ.get("PLAN", "free")).lower().strip()
    return plan in ("paid", "pro", "premium")

def pick_style(character: str, style_mode: str) -> str:
    # 🎨 알록이/달록이 스타일 분기
    base = "soft, warm, high-quality, cute, storybook illustration, clean background"
    if character == "알록이":
        char = "Alloki, a fluffy baby poodle with pastel rainbow fur"
    else:
        char = "Dalloki, a fluffy baby poodle with pastel rainbow fur"

    if style_mode == "일상존":
        return f"{char}, cozy daily life scene, {base}"
    if style_mode == "계절 무지개존":
        return f"{char}, seasonal rainbow mood, subtle seasonal background, {base}"
    if style_mode == "무지개 나라 베이커리존":
        return f"{char}, rainbow bakery kingdom theme, cute pastries, {base}"
    return f"{char}, {base}"

def season_pack_branch() -> str:
    # ✅ 시즌팩 분기(샘플)
    # 여기 규칙을 더 바꿀 수 있어
    m = time.localtime().tm_mon
    if m in (3,4,5):
        return "spring"
    if m in (6,7,8):
        return "summer"
    if m in (9,10,11):
        return "autumn"
    return "winter"

# ---------------------------
# “진짜 이미지 생성” 함수
# (여기서 OpenAI 이미지 API 호출)
# ---------------------------
def generate_real_image(prompt: str) -> bytes:
    """
    반환: PNG bytes
    주의:
    - requirements.txt에 openai가 있어야 함: openai>=1.0.0
    - Streamlit secrets에 OPENAI_API_KEY 설정 필요
    """
    from openai import OpenAI

    api_key = st.secrets.get("OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY", "")).strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY가 없습니다. Streamlit Secrets에 OPENAI_API_KEY를 넣어주세요.")

    client = OpenAI(api_key=api_key)

    # 모델은 너 프로젝트에서 쓰는 걸로 유지 (예: gpt-image-1)
    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024",
    )

    # SDK 버전에 따라 응답 형태가 다를 수 있어서 안전 처리
    # 일반적으로 b64_json 또는 bytes 형태로 제공됨
    img = result.data[0]
    if hasattr(img, "b64_json") and img.b64_json:
        import base64
        return base64.b64decode(img.b64_json)

    # 혹시 url로 오는 경우(환경에 따라) 다운로드
    if hasattr(img, "url") and img.url:
        import requests
        r = requests.get(img.url, timeout=60)
        r.raise_for_status()
        return r.content

    raise RuntimeError("이미지 생성 결과를 해석할 수 없습니다. (b64_json/url 없음)")

def generate_text_copy(character: str, season: str, paid: bool) -> str:
    # 🧠 문구 생성 (간단 버전)
    # 나중에 GPT 텍스트로 진짜 생성도 연결 가능
    if not paid:
        return f"[무료] {character} · {season} 오늘의 한 줄: ‘조금만 해도 충분해’"
    return f"[유료] {character} · {season} 오늘의 한 줄: ‘지금의 나를 응원해’"

def run_flow(character: str):
    paid = is_paid_user()
    season = season_pack_branch()

    st.info(f"선택: {character} / 시즌: {season} / 플랜: {'유료' if paid else '무료'}")

    style_mode = st.session_state.get("style_mode", "일상존")
    prompt = pick_style(character, style_mode)

    # 무료/유료 제한 예시
    if (not paid) and style_mode == "무지개 나라 베이커리존":
        st.warning("무료 플랜에서는 ‘무지개 나라 베이커리존’이 제한됩니다. (유료에서만 가능)")
        return

    with st.spinner("🎨 진짜 이미지 생성 중..."):
        png_bytes = generate_real_image(prompt)

    st.image(png_bytes, caption=f"{character} ({style_mode})", use_container_width=True)

    copy = generate_text_copy(character, season, paid)
    st.success("🧠 문구 생성 완료")
    st.write(copy)

    st.divider()
    st.subheader("🎬 영상 생성 연결(준비중)")
    st.caption("여기는 다음 단계: 이미지+문구를 기반으로 영상 생성 파이프라인을 연결하는 자리예요.")
    st.button("🎬 영상 만들기(준비중)", disabled=True)

# ---------------------------
# UI
# ---------------------------
st.title("🐼 알록이 & 달록이 앱")
st.caption("Streamlit 배포 성공 🎉")
st.write("이제 여기에 기능을 하나씩 붙이면 됩니다.")

# 🎨 스타일 선택
style_mode = st.selectbox(
    "🎨 테마 선택",
    ["일상존", "계절 무지개존", "무지개 나라 베이커리존"],
    index=0
)
st.session_state["style_mode"] = style_mode

# ✅ 여기서부터 버튼 2개는 무조건 보임(세로)
# ✅ 버튼은 columns로 강제 분리 (Streamlit 안정 패턴)
col1, col2 = st.columns(2)

with col1:
    if st.button("🐼 알록이 시작하기", use_container_width=True, key="btn_alloki"):
        run_flow("알록이")

with col2:
    if st.button("🐼 달록이 시작하기", use_container_width=True, key="btn_dalloki"):
        run_flow("달록이")

