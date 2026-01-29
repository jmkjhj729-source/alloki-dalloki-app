import streamlit as st

st.set_page_config(page_title="알록이 & 달록이 앱", page_icon="🐼", layout="centered")

st.title("🐼 알록이 & 달록이 앱 (버튼 테스트)")
st.caption("지금은 '버튼 2개가 화면에 뜨는지'만 확인합니다.")

# 화면에 실제로 새 코드가 떠 있는지 확인용 표시
st.info("✅ DIAG: app.py가 이 코드로 실행 중입니다. (이 글이 보이면 반영 성공)")

st.divider()

col1, col2 = st.columns(2)
with col1:
    if st.button("🐼 알록이 시작하기", use_container_width=True, key="btn_alloki"):
        st.success("알록이 버튼 클릭됨 ✅")

with col2:
    if st.button("🐼 달록이 시작하기", use_container_width=True, key="btn_dalloki"):
        st.success("달록이 버튼 클릭됨 ✅")

st.divider()
st.write("세션 상태:", dict(st.session_state))
