@echo off
cd /d "%~dp0"
python -m pip install --upgrade pip >nul 2>nul
python -m pip install -r requirements_user.txt
streamlit run ui_streamlit.py
pause
