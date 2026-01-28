# ☁️ 다른 와이파이/PC 꺼져도 접속되게 만드는 방법 (클라우드 배포)

요구사항:
- ✅ 다른 와이파이에서도 접속
- ✅ PC가 꺼져도 접속(=항상 켜져있는 서버 필요)
- ✅ 휴대폰/PC 각각 따로 실행 가능

가장 현실적인 2가지 루트:

## 루트 A) "클라우드에 올려서" 항상 켜두기 (추천)
- Render / Fly.io / Railway / VPS 중 하나
- 접속 URL이 고정됨: https://xxxx.onrender.com 같은 형태
- APP_PASSWORD로 비밀번호 걸기 권장

### 1) Render(가장 쉬움)
1. 이 폴더를 GitHub에 업로드
2. Render에서 New > Web Service
3. Build Command: `pip install -r requirements_user.txt`
4. Start Command: `streamlit run ui_streamlit.py --server.address 0.0.0.0 --server.port $PORT --server.headless true`
5. Environment Variables:
   - `APP_PASSWORD` = 원하는 비밀번호
6. Deploy

### 2) Docker로 어디든 배포(범용)
로컬에서 테스트:
```bash
docker compose up --build
```
서버에서 동일하게 실행하면 외부 접속 가능.

> 보안: 공개 배포 시 APP_PASSWORD를 반드시 설정하세요.

---

## 루트 B) "내 PC/폰에서 각각 따로 실행"
- PC: START_USER_UI.bat / START_USER_UI_MOBILE.bat 그대로 사용
- Android 폰: Termux(Python 설치)로 실행 가능 (iPhone은 제한이 큼)

Android(개념):
1) Termux 설치
2) `pkg install python`
3) `pip install -r requirements_user.txt`
4) `streamlit run ui_streamlit.py --server.port 8501 --server.address 127.0.0.1`
5) 폰 브라우저에서 `http://127.0.0.1:8501`

---

## 중요
- "다른 와이파이" + "PC 꺼져도" = **클라우드 배포가 필수**입니다.
- ngrok/Cloudflare Tunnel은 PC가 켜져 있어야 해서 조건을 만족하지 못해요.


[모드]
- 혼자 쓰기: APP_PASSWORD 설정, PUBLIC_DEMO=0
- 공개 체험: PUBLIC_DEMO=1 + (유료해제) PAID_MASTER_KEY 또는 LICENSE_KEYS
