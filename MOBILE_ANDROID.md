# 📱 Android에서 폰 단독 실행(로컬)

iOS는 시스템 제약 때문에 같은 방식이 어렵습니다.
Android는 Termux로 가능해요.

## 1) Termux 설치
- F-Droid 권장(Play Store 버전은 오래됨)

## 2) Python 설치
```bash
pkg update
pkg install python git
```

## 3) 프로젝트 복사
- zip을 폰에 넣고 압축 해제하거나
- git clone으로 받기

## 4) 실행
```bash
pip install -r requirements_user.txt
streamlit run ui_streamlit.py --server.address 127.0.0.1 --server.port 8501
```
브라우저에서:
- http://127.0.0.1:8501
