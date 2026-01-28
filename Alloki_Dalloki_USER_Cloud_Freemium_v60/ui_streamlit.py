
# -------------------- PLAN_MODE_SELECTOR --------------------
if APP_PASSWORD and not PUBLIC_DEMO:
    st.sidebar.subheader("🔐 접속 비밀번호")
    pw = st.sidebar.text_input("Password", type="password")
    if pw != APP_PASSWORD:
        st.warning("비밀번호를 입력해야 사용할 수 있어요.")
        st.stop()

plan = "paid"
paid_unlocked = True
if PUBLIC_DEMO:
    st.sidebar.subheader("🧪 체험/유료 선택")
    plan = st.sidebar.radio("플랜", ["무료 체험", "유료(키 입력)"], index=0)
    if plan == "유료(키 입력)":
        key = st.sidebar.text_input("라이선스 키", type="password")
        paid_unlocked = False
        if key and ((PAID_MASTER_KEY and key == PAID_MASTER_KEY) or (LICENSE_KEYS and key in LICENSE_KEYS)):
            paid_unlocked = True
    else:
        paid_unlocked = False
# ------------------ END PLAN_MODE_SELECTOR ------------------
# -*- coding: utf-8 -*-
"""
Streamlit UI (USER Edition)
Run:
  streamlit run ui_streamlit.py
"""
import os
import subprocess
import sys
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "user_assets"
ASSETS.mkdir(parents=True, exist_ok=True)
OUT = ROOT / "out_user"
OUT.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="알록이·달록이 1인 운세 편집 시스템 (USER)", layout="wide")

# ===================== FREEMIUM_CONFIG =====================
PUBLIC_DEMO = os.environ.get("PUBLIC_DEMO", "0").strip() == "1"
APP_PASSWORD = os.environ.get("APP_PASSWORD", "").strip()
PAID_MASTER_KEY = os.environ.get("PAID_MASTER_KEY", "").strip()
LICENSE_KEYS = [k.strip() for k in os.environ.get("LICENSE_KEYS", "").split(",") if k.strip()]

FREE_MAX_DAYS = int(os.environ.get("FREE_MAX_DAYS", "1"))
FREE_DISABLE_ZIP = os.environ.get("FREE_DISABLE_ZIP", "1").strip() == "1"
FREE_FORCE_WATERMARK = os.environ.get("FREE_FORCE_WATERMARK", "1").strip() == "1"
FREE_LOCK_REST = os.environ.get("FREE_LOCK_REST", "1").strip() == "1"
# =================== END FREEMIUM_CONFIG ===================

