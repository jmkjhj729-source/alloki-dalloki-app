# ✅ 버튼은 columns로 강제 분리 (Streamlit 안정 패턴)
col1, col2 = st.columns(2)

with col1:
    if st.button("🐼 알록이 시작하기", use_container_width=True, key="btn_alloki"):
        run_flow("알록이")

with col2:
    if st.button("🐼 달록이 시작하기", use_container_width=True, key="btn_dalloki"):
        run_flow("달록이")
