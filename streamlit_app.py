import streamlit as st
import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
V60_DIR = ROOT / "Alloki_Dalloki_USER_Cloud_Freemium_v60"
V60_APP = V60_DIR / "app.py"

st.set_page_config(page_title="알록이 & 달록이", layout="centered")

st.title("🐼 알록이 & 달록이 앱")
st.write("Streamlit 배포 성공 🎉")

st.info("이제 여기에 UI를 하나씩 붙이면 됩니다.")
if st.button("🐼 알록이 시작하기"):
    st.write("v60 실행중... 잠시만요 🐾")

    # ✅ 먼저 '테스트용'으로 v60 도움말(-h) 실행 (정상 연결 확인용)
    cmd = [
    sys.executable,
    str(V60_APP),
    "run_week",
    "--season", "spring"
]


    result = subprocess.run(
        cmd,
        cwd=str(V60_DIR),              # ✅ v60 폴더에서 실행 (중요)
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        st.success("✅ v60 연결 성공! (도움말 출력)")
        st.code(result.stdout)
    else:
        st.error("❌ v60 실행 실패")
        st.code(result.stderr)

