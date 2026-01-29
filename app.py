import streamlit as st

# ===============================
# 기본 설정
# ===============================
st.set_page_config(
    page_title="알록이 & 달록이 앱",
    page_icon="🐼",
    layout="centered"
)

# ===============================
# 타이틀
# ===============================
st.title("🐼 알록이 & 달록이 앱")
st.caption("Streamlit 배포 성공 🎉")
st.write("아래 버튼이 보이면 정상입니다.")

st.divider()

# ===============================
# 테마 선택
# ===============================
style_mode = st.selectbox(
    "🎨 테마 선택",
    ["일상존", "계절 무지개존", "무지개 나라 베이커리존"],
    index=0
)

st.divider()

# ===============================
# 버튼 영역
# ===============================
col1, col2 = st.columns(2)

with col1:
    if st.button("🐼 알록이 시작하기", use_container_width=True):
        st.success("알록이 버튼 클릭 성공!")
        st.write(f"선택된 테마: {style_mode}")
        st.image(
            "https://placekitten.com/400/400",
            caption="(테스트용 이미지 – 알록이)"
        )

with col2:
    if st.button("🐼 달록이 시작하기", use_container_width=True):
        st.success("달록이 버튼 클릭 성공!")
        st.write(f"선택된 테마: {style_mode}")
        st.image(
            "https://placebear.com/400/400",
            caption="(테스트용 이미지 – 달록이)"
        )

st.divider()

st.caption("✅ 여기까지 보이면 app.py 연결은 100% 성공입니다.")
