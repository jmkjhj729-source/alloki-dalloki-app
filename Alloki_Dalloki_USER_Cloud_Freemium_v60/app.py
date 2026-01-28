# app.py
import streamlit as st
import run_generate

st.set_page_config(page_title="알록이 & 달록이 앱", page_icon="🐼", layout="centered")

st.title("🐼 알록이 & 달록이 앱")
st.caption("버튼 클릭 → 문구 생성 / 시즌팩 분기 / 이미지 생성(샘플)")

user_name = st.text_input("이름", value="민경")
season = st.selectbox("시즌", ["spring", "summer", "autumn", "winter"])
offer_code = st.selectbox("플랜", ["D7", "D14", "D21", "SEASONPACK"])

st.write("---")

if st.button("🐼 알록이 시작하기"):
    with st.spinner("v60 실행중... 잠시만요 🧸"):
        result = run_generate.run_all(
            user_name=user_name,
            season=season,
            offer_code=offer_code,
            out_dir="outputs",
        )

    if not result.ok:
        st.error(result.msg)
    else:
        st.success(result.msg)

        st.subheader("✅ 시즌팩/플랜 분기 결과")
        st.write(f"- 시즌: **{result.season}**")
        st.write(f"- 플랜코드: **{result.offer_code}**")
        st.write(f"- 라벨: **{result.plan_label}**")

        st.subheader("✅ 문구(A/B/C)")
        st.write(result.copy)

        st.subheader("✅ 생성된 이미지(샘플)")
        if result.image_path:
            st.image(result.image_path, use_container_width=True)
            st.code(result.image_path)
        else:
            st.warning("이미지 파일이 생성되지 않았어요.")
