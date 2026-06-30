# BeautyScope — 화장품 리뷰 분석 서비스

쿠팡·무신사·올리브영 3개 플랫폼 리뷰 538,774건을 수집·분석해  
상품별 속성(보습/향/자극 등) 장단점과 추천 순위를 제공하는 Streamlit 서비스.

---

## 실행 방법

**Python 3.10 이상** 필요. Git 불필요.

1. [Releases](../../releases) 에서 `BeautyScope_실행패키지.zip` 다운로드
2. 압축 해제 후 폴더 안에서:

```
python run.py
```

브라우저가 자동으로 열립니다.

---

## 폴더 구조

```
1_source/                        소스코드 + 원본 데이터
├── pipeline/
│   ├── coupang_crawler.py       쿠팡 리뷰 크롤러
│   ├── merge_datasets.py        3개 플랫폼 데이터 통합
│   ├── precompute_model_sentiment.py   ML 모델 배치 추론
│   ├── precompute_absa.py       속성 감성 집계
│   ├── precompute_skin_segments.py     피부타입 세그먼트 집계
│   └── precompute_dashboard.py  대시보드 통계 집계
├── train/
│   ├── ml/  TF-IDF + LogisticRegression 학습
│   └── dl/  FFNN / LSTM / KoELECTRA 학습
└── merged_reviews_all.csv       통합 원본 데이터 268MB (Git LFS)

2_executable/                    실행 파일 + 데이터 + 모델
├── run.py                       실행 스크립트 (python run.py)
├── app.py                       Streamlit 앱
├── absa.py                      속성 감성 분석 규칙
├── report_data.py               데이터 조회·가공
├── model_utils.py               모델 유틸
├── preprocessing_ko.py          형태소분석 래퍼
├── requirements.txt
└── models/
    ├── ml_logreg.joblib         학습된 ML 모델
    ├── tfidf_vectorizer.joblib
    ├── aspect_sentiment.csv     상품별 속성 집계 결과
    ├── product_summary.csv
    └── ...

3_docs/                          문서
├── 발표_피드백.md
├── 테크니컬_리포트.md
└── 시연영상.mp4
```

---

## 모델이 실제로 하는 일

"모델을 만들라니까 만든 느낌"이라는 피드백을 반영해 개선했습니다.

학습된 감성분석 모델(정확도 0.738)이 **화면에 보이는 장단점 %와 추천 순위를 직접 바꿉니다.**  
별점과 리뷰 내용이 불일치한다고 판단한 리뷰 **50,806건(9.5%)** 을 집계에서 제외하고  
나머지 483,997건으로 재계산 — 모델을 빼면 다른 숫자가 나옵니다.

자세한 내용: [3_docs/발표_피드백.md](3_docs/발표_피드백.md)
