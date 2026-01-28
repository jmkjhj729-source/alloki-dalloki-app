@echo off
cd /d "%~dp0"
python -m pip install --upgrade pip >nul 2>nul
python -m pip install -r requirements_user.txt

REM 📱 Mobile access (same Wi‑Fi):
REM Run this, then open on phone: http://<PC_IP>:8501
REM Find PC_IP by running: python show_phone_url.py  (or ipconfig)

streamlit run ui_streamlit.py --server.address 0.0.0.0 --server.port 8501 --server.headless true
pause
