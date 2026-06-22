# BeautyScope 개발 기록

> 화장품 리뷰 크롤링 데이터로 감성 분류 모델을 만들고, Streamlit으로 서비스까지
> 구현한 과정의 기록. 발표용 정리 문서.

## 1. 서비스 개요

**BeautyScope**: 쿠팡·무신사·올리브영 3개 플랫폼의 화장품 리뷰를 학습해
리뷰 텍스트의 감성(긍정/중립/부정)을 분류하는 Streamlit 웹 서비스.

- 리뷰를 입력하면 ML/DL 두 모델이 동시에 예측 결과를 보여줌
- 538,774건 데이터 기반 통계 대시보드 (플랫폼/카테고리별 분포, 트렌드, 키워드)

## 2. 데이터 준비 단계 (가장 시간이 많이 든 단계)

### 2-1. 1차 수집 — 쿠팡 단독 (86,379건)
- 20개 키워드로 쿠팡 화장품 리뷰 크롤링, 별점 기반 sentiment 라벨 부여
  (4~5점=positive, 3점=neutral, 1~2점=negative)
- **문제**: 체험단/협찬/도배성 리뷰가 섞여 있어 노이즈가 심함
- **해결**: `remove_noise.py`, `quality_check.py`로 패턴 기반 필터링 후
  112,971건 → 86,380건으로 정제

### 2-2. 데이터 추가 확보 — 다른 사람이 크롤링한 데이터 통합
연구 규모를 늘리기 위해 동료가 크롤링한 무신사(231,029건)·올리브영(221,525건,
JSONL 4개 파일) 데이터를 추가로 확보. **이 단계에서 컬럼 스키마가 셋 다 다 달라서
바로 합칠 수 없었음** — 이게 가장 까다로운 부분이었다.

| 문제 | 내용 | 해결 |
|---|---|---|
| 컬럼명 불일치 | 쿠팡 `review_content`/무신사 `review_text`/올리브영 JSON 키 다름 | 공통 스키마(`platform, product_id, rating, sentiment, review_content, review_date` 등)로 통일하는 매핑 스크립트 작성 |
| **sentiment 라벨 기준 불일치 (가장 중요)** | 무신사의 `sentiment` 컬럼은 별점이 아니라 **리뷰 텍스트 분석 기반**이었음. 확인해보니 5점 리뷰의 21%가 `부정`으로 라벨링되어 있었음 (`rating=5` & `sentiment=부정` 42,869건) | 신뢰할 수 없는 라벨이라 판단, **모든 데이터의 sentiment를 별점에서 일괄 재계산**해서 기준을 통일. 원본 라벨은 `sentiment_text_raw`로 보존만 함 |
| 인코딩 문제 | 무신사 CSV가 BOM 포함 UTF-8(`utf-8-sig`)인데 기본 인코딩으로 읽으면 한글이 깨짐(mojibake) | `encoding='utf-8-sig'` 명시 |
| 형식 불일치 | 올리브영은 CSV가 아니라 JSONL 4개 파일(카테고리별), 쿠팡/무신사는 CSV | 파일별 로더 함수를 따로 만들어 통일 스키마로 변환 후 `pd.concat` |
| 중복 리뷰 | 같은 리뷰가 여러 크롤링 시점에 중복 수집됨 | `product_id+nickname+date+content` 기준 `drop_duplicates` (1,085건 제거) |

최종 통합 데이터: **538,774건** (`merge_datasets.py`로 재현 가능)

| 플랫폼 | 건수 |
|---|---|
| 무신사 | 230,870 |
| 올리브영 | 221,525 |
| 쿠팡 | 86,379 |

### 2-3. 클래스 불균형 문제
- 통합 후 positive 86.7%, negative 8.2%, neutral 5.1% — 이대로 학습하면
  모델이 전부 positive로 찍어도 86%대 정확도가 나와서 무의미한 모델이 됨
- **해결**: negative/neutral 전량 + positive는 negative의 2배 규모로만
  다운샘플링 (`ml/prepare_data.py`) → 학습셋 160,176건 (positive 88,572 /
  negative 44,286 / neutral 27,318)

## 3. 모델 — ML과 DL을 나눠서 비교

### 3-1. 환경 제약 (예상치 못한 불편함)
- 원래 PyTorch로 LSTM/BERT 계열 파인튜닝을 하려 했는데, **이 환경의 Python이
  3.14라서 PyTorch/TensorFlow 휠이 아직 배포되지 않아 설치 자체가 실패**
  (`pip install torch` → `No matching distribution found`)
- 다른 파이썬 버전도 환경에 없어서 venv 교체도 불가능
- **해결**: 신경망 프레임워크 없이 **numpy로 순전파/역전파를 직접 구현**해서
  DL 모델을 만듦. 오히려 "신경망이 내부적으로 어떻게 학습되는지"를 발표에서
  더 명확히 설명할 수 있는 소재가 됨

### 3-2. ML 모델 — TF-IDF + LogisticRegression
- 형태소 분석기(konlpy)는 자바 의존성이 있어 설치가 무거워서, 1~2gram 음절
  단위 TF-IDF(`max_features=20000`)로 대체 (별도 설치 없이 비슷한 효과)
- `class_weight='balanced'`로 불균형 보정
- 학습 시간 6.6초 (CPU)
- **결과: accuracy 0.738 / macro F1 0.677**

```
              precision    recall  f1-score   support
    negative       0.75      0.72      0.74      6547
     neutral       0.39      0.53      0.45      4056
    positive       0.89      0.81      0.85     13423
```

### 3-3. DL 모델 — numpy 피드포워드 신경망 (직접 구현)
**신경망 구조**: TF-IDF(20,000차원) → Dense(128, ReLU) → Dense(64, ReLU) →
Dense(3, Softmax)

**학습 방식**:
- Mini-batch SGD + momentum(0.9), L2 정규화
- learning rate 0.08에서 epoch마다 0.92배 감소
- batch size 256, 15 epoch, 학습 시간 약 132초
- loss: cross entropy

**구현 포인트**: TF-IDF가 sparse 행렬이라 numpy 기본으론 처리가 안 돼서
scipy sparse와 dense 배열 간 행렬곱(`X @ W1`, `X.T.dot(delta)`)을 직접
backprop 수식에 맞춰 구현함.

**결과: accuracy 0.762 / macro F1 0.663**

```
              precision    recall  f1-score   support
    negative       0.73      0.76      0.75      6547
     neutral       0.44      0.32      0.37      4056
    positive       0.84      0.89      0.87     13423
```

**관찰한 점**: epoch 4 부근(test_acc 0.781)을 찍고 이후로는 train loss는
계속 떨어지는데 test accuracy는 오히려 진동/하락 — **과적합 패턴**을 직접
확인함. 다음 개선으로 early stopping이나 dropout 추가가 필요하다는 결론.

### 3-4. ML vs DL 비교
| | accuracy | macro F1 | 학습시간 |
|---|---|---|---|
| ML (LogReg) | 0.738 | **0.677** | 6.6s |
| DL (직접 구현 NN) | **0.762** | 0.663 | 132s |

단순 TF-IDF 특징에서는 가벼운 로지스틱 회귀가 매크로 F1 기준으로 더 안정적이고,
신경망은 정확도는 약간 높지만 과적합 경향이 있어 클래스 불균형(neutral)에는
더 취약했음. neutral 클래스가 항상 가장 어려운 클래스였는데, 이는 "중립" 자체가
별점 3점이라는 모호한 기준에서 나온 라벨이라 텍스트 신호가 약한 것이 근본 원인.

## 4. 서비스 구현 (Streamlit)

- `app.py`: 3개 탭 구성
  1. 리뷰 감성 분석 데모 — 텍스트 입력 → ML/DL 동시 예측 + 확률 시각화
  2. 데이터 대시보드 — 플랫폼별 분포, 별점 분포, 월별 트렌드, 카테고리별
     감성 비율, 부정/긍정 다빈도 키워드, 리뷰 샘플 탐색
  3. 프로젝트 소개
- **문제**: 538,774건 원본 CSV를 대시보드 로딩 시마다 읽으면 느림
- **해결**: `precompute_dashboard.py`로 집계 결과를 미리 작은 CSV로 만들어두고
  대시보드는 그 집계 파일만 읽도록 분리 (`@st.cache_data`로 추가 캐싱)
- 로컬에서 `streamlit run app.py` 구동 후 HTTP 200 확인, 텍스트 입력 →
  ML/DL 예측 정상 동작 확인

## 5. 배포 준비
- `requirements.txt`로 의존성 고정 (scikit-learn, streamlit, pandas, numpy, scipy, joblib)
- 모델 파일(`models/*.joblib`, `models/dl_ffnn.npz`)과 집계 데이터(`models/agg_*.csv`)를
  리포에 포함해 별도 학습 없이 바로 서비스 구동 가능하게 구성
- 대용량 원본 크롤링 CSV(`coupang_reviews_*.csv` 등)는 `.gitignore`로 제외,
  최종 정제 데이터(`merged_reviews_all.csv`)만 추적 (용량 문제로 Git LFS 또는
  외부 스토리지 연동이 다음 단계 과제)

## 6. 발표 핵심 요약 (5분용)
1. 문제: 화장품 리뷰가 많은데 다 읽기 어려움 → 감성 자동 분류로 한눈에 파악
2. 데이터: 3개 플랫폼 합쳐 538,774건, 가장 큰 난관은 라벨 기준 통일
   (무신사 sentiment가 별점과 안 맞았던 것)
3. 모델: 환경 제약(Python 3.14, PyTorch 설치 불가)으로 numpy 직접 구현
   신경망과 ML 베이스라인을 병행 개발, 직접 비교
4. 결과: ML 0.738 acc / DL 0.762 acc, neutral 클래스가 공통적으로 어려움
5. 서비스: Streamlit으로 실시간 데모 + 데이터 대시보드 구현, 로컬 구동 검증 완료
