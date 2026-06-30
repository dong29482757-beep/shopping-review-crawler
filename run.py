"""
BeautyScope 실행 스크립트
python run.py
"""
import subprocess
import sys

print("패키지 설치 중...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"])

print("서비스 시작... (브라우저가 자동으로 열립니다)")
subprocess.call([sys.executable, "-m", "streamlit", "run", "app.py"])
