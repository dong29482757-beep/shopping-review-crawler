#!/bin/bash
echo ""
echo " BeautyScope - 화장품 리뷰 분석 서비스"
echo " ========================================"

# Python 설치 확인
if ! command -v python3 &> /dev/null; then
    echo ""
    echo " [오류] python3가 설치되어 있지 않습니다."
    echo " https://www.python.org 에서 Python 3.10 이상을 설치한 뒤 다시 실행하세요."
    exit 1
fi

# 가상환경 생성 (최초 1회)
if [ ! -d "venv" ]; then
    echo " [1/3] 가상환경 생성 중..."
    python3 -m venv venv
fi

# 패키지 설치
echo " [2/3] 패키지 설치 중..."
source venv/bin/activate
pip install -r requirements.txt -q

# 앱 실행
echo " [3/3] 서비스 시작..."
echo ""
echo " 브라우저가 자동으로 열립니다. (http://localhost:8501)"
echo " 종료하려면 Ctrl+C 를 누르세요."
echo ""
streamlit run app.py
