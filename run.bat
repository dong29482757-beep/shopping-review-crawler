@echo off
REM BeautyScope 실행 스크립트 (Windows)
REM 1) 가상환경 생성 + 의존성 설치 (최초 1회)
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt

REM 2) Streamlit 앱 실행 (이미 학습된 모델/집계 데이터가 models/ 폴더에 포함되어 있어 재학습 불필요)
streamlit run app.py
