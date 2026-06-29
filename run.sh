#!/bin/bash
# BeautyScope 실행 스크립트 (macOS/Linux)
# 1) 가상환경 생성 + 의존성 설치 (최초 1회)
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt

# 2) Streamlit 앱 실행 (이미 학습된 모델/집계 데이터가 models/ 폴더에 포함되어 있어 재학습 불필요)
streamlit run app.py
