# BeautyScope — 화장품 리뷰 분석 서비스

쿠팡·무신사·올리브영 3개 플랫폼 리뷰 538,774건을 수집·분석해
상품별 속성(보습/향/자극 등) 장단점, 추천 순위, 대안 상품을 한 화면에 보여주는 Streamlit 서비스.

---

## 바로 실행하기

**Python 3.10 이상**만 설치돼 있으면 됩니다.

### 방법 A — 실행 패키지 (가장 간단)

1. [Releases](../../releases) 에서 `BeautyScope_실행패키지.zip` 다운로드
2. 압축 해제 후 폴더 안에서:

```
Windows : run.bat 더블클릭
Mac/Linux: bash run.sh
```

가상환경 생성 → 패키지 설치 → 브라우저 자동 실행까지 스크립트가 알아서 합니다.

### 방법 B — 저장소 클론

```bash
git clone https://github.com/dong29482757-beep/shopping-review-crawler.git
cd shopping-review-crawler
run.bat        # Windows
bash run.sh    # Mac/Linux
```

> `merged_reviews_all.csv`(268MB)는 Git LFS로 관리됩니다.
> 앱 실행에는 불필요하고(models/ 집계 결과만 사용), 파이프라인을 다시 돌릴 때만 필요합니다.

---

## 폴더 구조

```
shopping-review-crawler/
│
├── run.bat / run.sh              ← 실행 스크립트 (여기서 시작)
├── requirements.txt
│
├── app.py                        ← Streamlit 앱 진입점
├── absa.py                       ← 속성 감성 분석 규칙 (8개 속성 × 긍/부정)
├── report_data.py                ← 데이터 조회·가공 함수
├── model_utils.py                ← 모델 라벨·확률보정 상수
├── preprocessing_ko.py           ← Okt 형태소분석 래퍼
│
├── models/                       ← 앱이 읽는 사전계산 결과
│   ├── aspect_sentiment.csv      ← 상품별 속성 집계
│   ├── product_summary.csv       ← 상품 기본 정보
│   ├── representative_reviews.csv
│   ├── review_reliability.csv    ← 리뷰 신뢰도 (모델 기반)
│   ├── review_match_flags.csv    ← 리뷰 단위 일치 여부 (ABSA 필터링용)
│   ├── skin_*.csv                ← 피부타입별 세그먼트
│   ├── agg_*.csv                 ← 대시보드 집계
│   ├── ml_logreg.joblib          ← 학습된 ML 모델 (TF-IDF + LogReg)
│   ├── tfidf_vectorizer.joblib
│   ├── dl_ffnn.npz               ← FFNN 가중치
│   ├── lstm_model.pt             ← LSTM 모델
│   └── *_report.txt              ← 학습 결과 요약
│
├── merged_reviews_all.csv        ← 원본 통합 데이터 268MB (Git LFS)
│
├── coupang_crawler.py            ← 쿠팡 리뷰 크롤러 (Playwright)
├── merge_datasets.py             ← 3개 플랫폼 통합
├── precompute_absa.py            ← 속성 집계 배치
├── precompute_model_sentiment.py ← 모델 배치 추론
├── precompute_skin_segments.py   ← 피부타입 세그먼트 집계
├── precompute_dashboard.py       ← 대시보드 집계
│
├── ml/                           ← ML 모델 학습 코드
│   ├── prepare_data.py
│   ├── tokenize_data.py
│   └── train_ml.py
│
├── dl/                           ← DL 모델 학습 코드
│   ├── neural_net.py
│   ├── train_dl.py
│   ├── train_lstm.py
│   └── train_transformer.py
│
└── docs/
    ├── 발표_피드백.md
    ├── 테크니컬_리포트.md
    └── 시연영상.mp4
```

---

## 데이터 파이프라인 (재실행 방법)

앱 실행에는 불필요합니다. `models/`가 이미 계산된 결과를 담고 있습니다.
원본 데이터부터 다시 계산하려면 아래 순서대로 실행하세요.

```
1. coupang_crawler.py             → 쿠팡 리뷰 수집
2. merge_datasets.py              → 3개 플랫폼 통합 → merged_reviews_all.csv
3. ml/prepare_data.py             → 학습 데이터 준비
4. ml/train_ml.py                 → ML 모델 학습 → models/ml_logreg.joblib
5. precompute_model_sentiment.py  → 전체 리뷰 모델 추론 → models/review_match_flags.csv
6. precompute_absa.py             → 속성 집계 → models/aspect_sentiment.csv 등
7. precompute_skin_segments.py    → 피부타입 집계
8. precompute_dashboard.py        → 대시보드 집계
```

---

## 모델이 실제로 하는 일

> "모델을 만들긴 했는데 실사용성이 없다"는 피드백을 받고 두 차례 개선했습니다.

학습된 감성분석 모델(TF-IDF + LogisticRegression, 정확도 0.738)은 단순 참고 지표가 아니라
**앱이 보여주는 장단점 %와 추천 순위 자체를 계산하는 데 직접 쓰입니다.**

별점과 리뷰 내용이 불일치한다고 모델이 판단한 리뷰 **50,806건(전체의 9.5%)** 을
속성 집계에서 제외하고 나머지 483,997건으로 재계산 — 모델을 빼면 다른 숫자가 나옵니다.

자세한 내용은 [docs/발표_피드백.md](docs/발표_피드백.md), [docs/테크니컬_리포트.md](docs/테크니컬_리포트.md) 참고.
