# 🐶🌈 알록이·달록이 1인 운세 편집 시스템 (USER / 배포용)

✅ “코드 없이” 브라우저에서 바로 사용하는 배포판입니다.  
**실행 프로그램은 1개**: `START_USER_UI.bat` (윈도우) 또는 `streamlit run ui_streamlit.py`

---

## 윈도우 (추천)
1) 압축 해제
2) `START_USER_UI.bat` 더블클릭
3) 브라우저에서 PNG 업로드 → 생성 → ZIP 다운로드

## 맥/기타
```bash
pip install -r requirements_user.txt
streamlit run ui_streamlit.py
```

결과물은 `out_user/`에 생성됩니다.


---

## 📱 모바일(휴대폰)에서 보기 (같은 와이파이)
1) PC에서 `START_USER_UI_MOBILE.bat` 실행
2) PC에서 IP 확인: `python show_phone_url.py` 또는 `ipconfig`
3) 휴대폰 브라우저에서 접속: `http://PC_IP:8501`

⚠️ 주의: 같은 와이파이에 있는 기기만 접속 가능합니다. 실행 중에만 열립니다.


---

## ☁️ 다른 와이파이/PC 꺼져도 접속(클라우드)
`DEPLOY_CLOUD.md`를 참고하세요. (APP_PASSWORD로 비번 걸기 포함)
