# 🐶🌈 알록이·달록이 1인 운세 편집 시스템 (사용자용 배포판)

✅ 목적: 사용자가 **코드 없이** PNG를 넣고, 카드/썸네일/스토리 이미지를 생성해 SNS에 올릴 수 있게 하는 “편집 도구”

- 업로드/발송/웹훅/결제 연동은 기본 OFF (안전 배포)
- 결과물은 로컬 폴더(out_user)에 생성됩니다.

## 1) 윈도우: 더블클릭 실행
1) 압축 해제
2) `START_USER_UI.bat` 더블클릭
3) 브라우저에서 PNG 업로드 → “이번 주 세트 생성” 클릭

## 2) 수동 실행 (모든 OS)
```bash
pip install -r requirements_user.txt
streamlit run ui_streamlit.py
```

## 3) CLI 실행
```bash
python user_app.py generate_week --season spring --platforms instagram,tiktok --segments new,repeat
```

## 폴더
- `user_assets/` : alloki.png / dalloki.png / background.png(선택)
- `out_user/` : 생성 결과(이미지/ZIP/preview.html)
