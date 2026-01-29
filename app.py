import base64
import hashlib
import json
import os
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, Tuple

import requests
import streamlit as st


# =========================
# 기본 설정
# =========================
APP_TITLE = "🐼 알록이 & 달록이 앱"
DEFAULT_MODEL = "gpt-image-1"  # OpenAI Image API (진짜 이미지 생성)
OPENAI_IMAGE_ENDPOINT = "https://api.openai.com/v1/images/generations"

# 무료 제한(원하면 숫자 조절)
FREE_DAILY_LIMIT = 3

# 영상 생성(연결) - 프로젝트에 run_generate.py가 있는 경우만 실행 시도
VIDEO_SCRIPT_CANDIDATES = [
    "run_generate.py",
    "Alloki_Dalloki_USER_Cloud_Freemium_v60/run_generate.py",
]


# =========================
# 유틸
# =========================
def _sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def _today_key() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def get_secret(key: str, default: str = "") -> str:
    try:
        return str(st.secrets.get(key, default))
    except Exception:
        return default


def is_paid_mode() -> bool:
    plan = get_secret("PLAN", "free").strip().lower()
    return plan == "paid"


def premium_unlocked() -> bool:
    """
    PLAN=paid 이면 바로 True.
    PLAN=free 인 경우, 사용자가 PREMIUM_CODE를 입력하면 True.
    """
    if is_paid_mode():
        return True

    premium_code = get_secret("PREMIUM_CODE", "").strip()
    user_code = st.session_state.get("user_premium_code", "").strip()

    if not premium_code:
        return False  # 설정 자체가 없으면 잠금 상태 유지
    return user_code != "" and user_code == premium_code


def check_free_limit_or_block() -> Tuple[bool, str]:
    """
    무료일 때만 일일 제한 체크.
    반환: (가능여부, 메시지)
    """
    if premium_unlocked():
        return True, "✅ 유료(또는 프리미엄 해제) 상태입니다."

    # 무료 제한 카운터(간단 버전: 세션+일자 기준)
    day = _today_key()
    key = f"free_count::{day}"
    cnt = int(st.session_state.get(key, 0))

    if cnt >= FREE_DAILY_LIMIT:
        return False, f"❌ 무료 플랜은 하루 {FREE_DAILY_LIMIT}회까지 가능합니다. (오늘 사용: {cnt}회)"

    return True, f"🆓 무료 플랜 사용 가능 (오늘 {cnt}/{FREE_DAILY_LIMIT})"


def bump_free_count():
    day = _today_key()
    key = f"free_count::{day}"
    st.session_state[key] = int(st.session_state.get(key, 0)) + 1


# =========================
# 카피(문구) 생성: 시즌팩/기본 분기
# =========================
def season_kr(season: str) -> str:
    return {"spring": "봄", "summer": "여름", "autumn": "가을", "winter": "겨울"}.get(season, "시즌")


def copy_pack_for_offer(offer_code: str, season: str) -> Dict[str, str]:
    oc = (offer_code or "").upper()
    if oc == "SEASONPACK":
        sk = season_kr(season)
        # A=공감형, B=긴급형, C=프리미엄형
        return {
            "A": f"{sk} 시즌팩 21+3 · 오늘의 마음을 꺼내요 ✨",
            "B": f"{sk} 시즌팩 21+3 · 지금 안 사면 늦어요 ⏳",
            "C": f"{sk} 시즌팩 21+3 · 프리미엄 한정 💎",
        }

    # 기본(테마별)
    return {
        "A": "알록이&달록이 · 오늘의 감성 한 장 🫧",
        "B": "지금 바로 생성! 놓치면 후회 😵‍💫",
        "C": "고화질 프리미엄 스타일로 뽑기 ✨",
    }


# =========================
# 진짜 이미지 생성(OpenAI Image API /v1/images/generations)
# - requests만 사용 (requirements 수정 없이 작동)
# - docs: https://platform.openai.com/docs/guides/image-generation
# =========================
@dataclass
class ImageResult:
    bytes_data: bytes
    prompt_used: str
    revised_prompt: Optional[str] = None


def openai_generate_image(prompt: str, size: str = "1024x1024", quality: str = "high") -> ImageResult:
    api_key = get_secret("OPENAI_API_KEY", "").strip()
    if not api_key or not api_key.startswith("sk-"):
        raise RuntimeError("OPENAI_API_KEY가 없거나 형식이 이상해요. (Secrets에 sk-로 시작하는 키를 넣어주세요)")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": DEFAULT_MODEL,
        "prompt": prompt,
        "size": size,
        # quality는 모델/계정 설정에 따라 지원 범위가 다를 수 있어 안전하게 포함
        "quality": quality,
        "n": 1,
    }

    r = requests.post(OPENAI_IMAGE_ENDPOINT, headers=headers, data=json.dumps(payload), timeout=120)
    if r.status_code != 200:
        raise RuntimeError(f"이미지 생성 실패: HTTP {r.status_code}\n{r.text}")

    data = r.json()
    b64 = data["data"][0].get("b64_json")
    if not b64:
        raise RuntimeError("응답에 b64_json이 없어요. (모델/권한/요청 파라미터 확인 필요)")

    img_bytes = base64.b64decode(b64)
    revised = data["data"][0].get("revised_prompt")
    return ImageResult(bytes_data=img_bytes, prompt_used=prompt, revised_prompt=revised)


# =========================
# 프롬프트 생성(알록이/달록이 + 테마 분기)
# =========================
def build_prompt(character: str, theme: str, season: str) -> str:
    """
    character: "알록이" or "달록이"
    theme: "일상존" | "계절 무지개존" | "무지개 나라 베이커리존"
    season: "spring|summer|autumn|winter"
    """
    # 캐릭터 기본 묘사
    if character == "알록이":
        char_desc = "a super cute baby poodle puppy named Alloki with fluffy pastel rainbow fur"
    else:
        char_desc = "a super cute baby poodle puppy named Dalloki with fluffy pastel rainbow fur"

    # 테마별 배경/소품
    if theme == "일상존":
        scene = (
            "cozy modern living room, warm daylight through a window, soft bokeh sparkles, "
            "realistic yet heartwarming, Disney-like illustration, ultra cute, high detail fur"
        )
    elif theme == "계절 무지개존":
        sk = season_kr(season)
        season_scene = {
            "spring": "spring vibe, soft cherry blossom petals floating, gentle pastel sky",
            "summer": "summer vibe, bright fresh light, minty breeze 느낌, tiny light particles",
            "autumn": "autumn vibe, warm amber sunlight, soft falling leaves bokeh",
            "winter": "winter vibe, cozy warm indoor light with subtle snow sparkle outside window",
        }.get(season, "season vibe")
        scene = (
            f"{sk} season rainbow theme, {season_scene}, pastel rainbow gradient background, "
            "soft bokeh sparkles, Disney-like illustration, high detail fur"
        )
    else:  # 무지개 나라 베이커리존
        scene = (
            "fantasy rainbow bakery world, cute pastries and cookies, warm soft lighting, "
            "pastel rainbow color palette, sparkly bokeh, Disney-like illustration, high detail fur"
        )

    # 캐릭터 1마리 단독으로 우선 생성(안정)
    prompt = (
        f"{char_desc}. {scene}. "
        "big round sparkling eyes fully open, short muzzle, tiny tongue, adorable smile. "
        "single cohesive illustration, no text, no watermark, high resolution."
    )
    return prompt


# =========================
# 영상 생성(연결): run_generate.py 있으면 실행 시도
# =========================
def find_video_script() -> Optional[str]:
    for p in VIDEO_SCRIPT_CANDIDATES:
        if os.path.exists(p):
            return p
    return None


def run_video_pipeline(character: str, theme: str) -> Tuple[bool, str]:
    script_path = find_video_script()
    if not script_path:
        return False, "run_generate.py를 찾지 못했어요. (프로젝트 경로/파일명 확인 필요)"

    # 안전: 실패해도 앱 안죽게 처리
    try:
        cmd = ["python", script_path, "--character", character, "--theme", theme]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if proc.returncode != 0:
            return False, f"영상 생성 스크립트 실행 실패\n\nSTDERR:\n{proc.stderr}\n\nSTDOUT:\n{proc.stdout}"
        return True, f"영상 생성 스크립트 실행 완료!\n\nSTDOUT:\n{proc.stdout}"
    except Exception as e:
        return False, f"영상 생성 실행 중 오류: {e}"


# =========================
# 핵심 플로우(버튼 클릭 시 실행)
# =========================
def run_flow(character: str):
    theme = st.session_state.get("theme", "일상존")
    season = st.session_state.get("season", "spring")

    # 무료/유료 제한 체크
    ok, msg = check_free_limit_or_block()
    st.info(msg)
    if not ok:
        st.stop()

    # 시즌팩 분기(계절 무지개존이면 시즌팩)
    offer_code = "SEASONPACK" if theme == "계절 무지개존" else "DEFAULT"
    copies = copy_pack_for_offer(offer_code, season)

    # 문구 선택 UI
    st.subheader("📝 문구 선택")
    colA, colB, colC = st.columns(3)
    with colA:
        pick_a = st.button("A안", use_container_width=True)
    with colB:
        pick_b = st.button("B안", use_container_width=True)
    with colC:
        pick_c = st.button("C안", use_container_width=True)

    # 기본값
    selected_key = st.session_state.get("selected_copy_key", "A")
    if pick_a:
        selected_key = "A"
    if pick_b:
        selected_key = "B"
    if pick_c:
        selected_key = "C"
    st.session_state["selected_copy_key"] = selected_key

    st.write(f"**선택된 문구({selected_key})**: {copies[selected_key]}")

    st.divider()

    # 진짜 이미지 생성
    st.subheader("🖼️ 진짜 이미지 생성")
    size = st.selectbox("사이즈", ["1024x1024", "1024x1536", "1536x1024"], index=0)
    quality = st.selectbox("퀄리티", ["high", "medium", "low"], index=0)

    prompt = build_prompt(character, theme, season)

    if st.button(f"✨ {character} 이미지 생성하기", use_container_width=True):
        with st.spinner("이미지 생성 중... (진짜 생성)"):
            try:
                res = openai_generate_image(prompt=prompt, size=size, quality=quality)
                if not premium_unlocked():
                    bump_free_count()

                st.success("✅ 이미지 생성 완료!")
                st.image(res.bytes_data, caption=f"{character} · {theme}", use_container_width=True)

                with st.expander("📌 사용된 프롬프트 보기"):
                    st.code(res.prompt_used)

                if res.revised_prompt:
                    with st.expander("🛠️ (옵션) 모델이 수정한 프롬프트"):
                        st.code(res.revised_prompt)

                st.divider()
                st.subheader("📦 결과 요약")
                st.write(f"- 캐릭터: **{character}**")
                st.write(f"- 테마: **{theme}**")
                if theme == "계절 무지개존":
                    st.write(f"- 시즌: **{season_kr(season)}**")
                st.write(f"- 문구: **{copies[selected_key]}**")

            except Exception as e:
                st.error(str(e))

    st.divider()

    # 영상 생성 연결(유료 권장)
    st.subheader("🎬 영상 생성 연결")
    st.caption("현재는 '연결'만 해둔 상태입니다. run_generate.py가 프로젝트에 있으면 실행을 시도합니다.")
    if st.button("🎥 영상 만들기(연결 실행)", use_container_width=True):
        if not premium_unlocked():
            st.warning("무료 플랜에서는 영상 생성 연결을 잠시 막아둘게요. (PLAN=paid 또는 PREMIUM_CODE로 해제)")
            st.stop()

        with st.spinner("영상 생성 파이프라인 실행 중..."):
            ok2, log = run_video_pipeline(character, theme)
            if ok2:
                st.success("✅ 영상 생성(연결) 실행 완료")
                st.text(log)
            else:
                st.error("❌ 영상 생성(연결) 실패")
                st.text(log)


# =========================
# UI
# =========================
def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🐼", layout="centered")
    st.title(APP_TITLE)
    st.caption("Streamlit 배포 성공 🎉")
    st.write("이제 여기에 기능을 하나씩 붙이면 됩니다.")

    # 프리미엄 입력(무료일 때만 표시)
    if not is_paid_mode():
        premium_code = get_secret("PREMIUM_CODE", "").strip()
        if premium_code:
            st.text_input("🔑 프리미엄 코드(있으면 입력)", key="user_premium_code", type="password")

    # 테마 선택
    st.subheader("🎨 스타일(테마) 선택")
    theme = st.selectbox("테마", ["일상존", "계절 무지개존", "무지개 나라 베이커리존"], index=0, key="theme")

    # 계절 무지개존이면 시즌 선택
    if theme == "계절 무지개존":
        season = st.selectbox("시즌 선택", ["spring", "summer", "autumn", "winter"], index=0, key="season")
        st.write(f"선택 시즌: **{season_kr(season)}**")
    else:
        st.session_state["season"] = "spring"

    st.divider()

    # ✅ 여기서 버튼 2개를 "무조건" 보여주기 (가장 안정)
    st.subheader("🚀 시작하기")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🐶 알록이 시작하기", use_container_width=True):
            st.session_state["active_character"] = "알록이"

    with col2:
        if st.button("🐶 달록이 시작하기", use_container_width=True):
            st.session_state["active_character"] = "달록이"

    # 버튼 눌렀을 때 아래에서 실행
    character = st.session_state.get("active_character")
    if character:
        st.divider()
        st.header(f"✅ {character} 플로우")
        run_flow(character)
    else:
        st.info("위에서 **알록이/달록이 시작하기** 버튼을 눌러주세요.")


if __name__ == "__main__":
    main()
