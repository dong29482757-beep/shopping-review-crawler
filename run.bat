@echo off
chcp 65001 > nul
echo.
echo  BeautyScope - 화장품 리뷰 분석 서비스
echo  ========================================

:: Python 설치 확인
python --version > nul 2>&1
if errorlevel 1 (
    echo.
    echo  [오류] Python이 설치되어 있지 않습니다.
    echo  https://www.python.org 에서 Python 3.10 이상을 설치한 뒤 다시 실행하세요.
    pause
    exit /b 1
)

:: 가상환경 생성 (최초 1회)
if not exist venv (
    echo  [1/3] 가상환경 생성 중...
    python -m venv venv
)

:: 패키지 설치
echo  [2/3] 패키지 설치 중...
call venv\Scripts\activate
pip install -r requirements.txt -q

:: 앱 실행
echo  [3/3] 서비스 시작...
echo.
echo  브라우저가 자동으로 열립니다. (http://localhost:8501)
echo  종료하려면 이 창에서 Ctrl+C 를 누르세요.
echo.
streamlit run app.py
