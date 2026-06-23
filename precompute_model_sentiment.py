"""
학습된 ML 모델(TF-IDF + 로지스틱회귀, 확률보정 적용)을 리뷰 전체에 돌려서
"별점 기반 라벨"과 "모델이 텍스트만 보고 판단한 라벨"이 얼마나 일치하는지
상품별로 집계한다.

별점 기반 라벨링의 한계(별점 5점인데 텍스트는 부정적인 경우가 21%)를
직접 검증/정량화하는 단계 — 상품별 "리뷰 신뢰도" 지표로 상품 리포트에
노출해서, 모델을 평가용으로만 두지 않고 서비스 품질 검증에 실제로 쓴다.

Okt 형태소분석이 병목이라(초당 약 200건) 534,803건 전체를 처리하는 데
시간이 걸리는 일회성 배치 작업이다. precompute_absa.py와 같은 모집단
(리뷰 20건 이상 상품)만 대상으로 한다.
"""
import time
import joblib
import numpy as np
import pandas as pd

from preprocessing_ko import clean_for_vectorizer
from model_utils import LABELS, PRIOR_CORRECTION

SRC = r"D:\crolling\merged_reviews_all.csv"
OUT_DIR = r"D:\crolling\models"
MIN_REVIEWS = 20


def correct_proba_batch(proba_matrix):
    corrected = proba_matrix * PRIOR_CORRECTION
    return corrected / corrected.sum(axis=1, keepdims=True)


def main():
    print("로딩...")
    df = pd.read_csv(SRC, low_memory=False).dropna(subset=["review_content", "sentiment"])

    review_counts = df.groupby(["platform", "product_id"]).size()
    valid_products = set(review_counts[review_counts >= MIN_REVIEWS].index)
    df["pp_key"] = list(zip(df["platform"], df["product_id"]))
    df = df[df["pp_key"].isin(valid_products)].reset_index(drop=True)
    print(f"대상 리뷰 수: {len(df)}")

    print("형태소 분석 + TF-IDF 토큰화 중 (Okt, 시간 오래 걸림)...")
    t0 = time.time()
    tokens = df["review_content"].apply(clean_for_vectorizer)
    print(f"토큰화 완료: {time.time()-t0:.1f}s")

    vec = joblib.load(f"{OUT_DIR}/tfidf_vectorizer.joblib")
    ml_model = joblib.load(f"{OUT_DIR}/ml_logreg.joblib")
    assert list(ml_model.classes_) == LABELS, "ml_model.classes_ 순서가 LABELS와 달라 보정이 깨짐"

    print("모델 예측 중...")
    t0 = time.time()
    X = vec.transform(tokens)
    proba_raw = ml_model.predict_proba(X)
    proba_corrected = correct_proba_batch(proba_raw)
    pred_idx = proba_corrected.argmax(axis=1)
    df["model_sentiment"] = np.array(LABELS)[pred_idx]
    df["model_confidence"] = proba_corrected.max(axis=1)
    print(f"예측 완료: {time.time()-t0:.1f}s")

    df["match"] = df["model_sentiment"] == df["sentiment"]

    reliability = (
        df.groupby(["platform", "product_id", "product_name"])
        .agg(
            review_count=("match", "size"),
            match_count=("match", "sum"),
        )
        .reset_index()
    )
    reliability["reliability_pct"] = (reliability["match_count"] / reliability["review_count"] * 100).round(1)
    reliability["mismatch_count"] = reliability["review_count"] - reliability["match_count"]
    reliability.to_csv(f"{OUT_DIR}/review_reliability.csv", index=False, encoding="utf-8-sig")

    print("저장 완료: review_reliability.csv")
    print(f"상품 수: {len(reliability)}")
    print(f"전체 평균 신뢰도: {reliability['reliability_pct'].mean():.1f}%")
    print(f"리뷰 단위 전체 일치율: {df['match'].mean()*100:.1f}%")


if __name__ == "__main__":
    main()
