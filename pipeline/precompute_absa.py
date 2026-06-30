"""
538,774건 전체 리뷰에 속성기반 감성분석을 적용해 상품별 집계를 만든다.
규칙 기반(absa.py)이라 Okt 형태소분석 없이 정규식만으로 처리 가능해서
전체 데이터에 적용해도 수십 초 내에 끝난다.

모델(precompute_model_sentiment.py)이 "별점과 리뷰 내용이 안 맞는다"고
판단한 리뷰는 여기서 실제로 제외한다 — 그래서 모델이 화면에 보이는 장단점
%와 추천 순위 자체를 바꾼다. review_match_flags.csv가 없으면(모델을 아직
안 돌렸으면) 필터링 없이 예전처럼 전체 리뷰로 계산한다.
"""
import os
import sys
import time
import collections
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from absa import extract_aspect_sentiments

SRC = os.path.join(ROOT, "merged_reviews_all.csv")
OUT_DIR = os.path.join(ROOT, "models")
MATCH_FLAGS_PATH = os.path.join(OUT_DIR, "review_match_flags.csv")

MIN_REVIEWS = 20  # 이 미만인 상품은 리포트 신뢰도가 낮아서 제외


def main():
    print("로딩...")
    df = pd.read_csv(SRC, low_memory=False).dropna(subset=["review_content", "sentiment"])
    df["category"] = df["category"].fillna("기타")  # groupby가 NaN 그룹을 통째로 드롭해서 무신사(category 없음)가 사라지는 문제 방지

    review_counts = df.groupby(["platform", "product_id"]).size()
    valid_products = set(review_counts[review_counts >= MIN_REVIEWS].index)
    print(f"전체 상품 {df['product_id'].nunique()}개 중 리뷰 {MIN_REVIEWS}건 이상: {len(valid_products)}개")

    df["pp_key"] = list(zip(df["platform"], df["product_id"]))
    df = df[df["pp_key"].isin(valid_products)]
    print(f"대상 리뷰 수: {len(df)}")

    excluded_count = 0
    if os.path.exists(MATCH_FLAGS_PATH):
        flags = pd.read_csv(MATCH_FLAGS_PATH, low_memory=False)
        # review_id가 (platform, product_id) 안에서 유일하지 않은 경우가 있어서
        # 컬럼 키로 merge하면 다대다로 폭발한다. precompute_model_sentiment.py가
        # 정확히 같은 필터(dropna 컬럼, MIN_REVIEWS)를 같은 원본 CSV에 같은 순서로
        # 적용해서 만든 파일이라, 두 결과의 행 순서가 1:1로 대응한다는 점을 이용해
        # 위치 기반으로 붙인다.
        before = len(df)
        if len(flags) != before:
            raise ValueError(
                f"review_match_flags.csv 행수({len(flags)})가 현재 필터링 결과({before})와 다릅니다. "
                "merged_reviews_all.csv나 MIN_REVIEWS가 바뀌었으면 precompute_model_sentiment.py를 다시 실행하세요."
            )
        df = df.reset_index(drop=True)
        df["match"] = flags["match"].values
        keep_mask = df["match"]
        excluded_count = int((~keep_mask).sum())
        df = df[keep_mask].drop(columns=["match"])
        print(f"모델 기반 필터링: {before}건 중 {excluded_count}건 제외(별점-내용 불일치 판정), {len(df)}건으로 계산")
    else:
        print("review_match_flags.csv 없음 — 필터링 없이 전체 리뷰로 계산 "
              "(precompute_model_sentiment.py를 먼저 실행하면 모델 기반 필터링이 적용됨)")

    t0 = time.time()
    rows = []
    for _, row in df.iterrows():
        mentions = extract_aspect_sentiments(row["review_content"], fallback_sentiment=row["sentiment"])
        for aspect, sentiment in mentions:
            rows.append((row["platform"], row["product_id"], row["product_name"], aspect, sentiment))
    print(f"속성 추출 완료: {time.time()-t0:.1f}s, mentions={len(rows)}")

    mentions_df = pd.DataFrame(rows, columns=["platform", "product_id", "product_name", "aspect", "sentiment"])
    agg = (
        mentions_df.groupby(["platform", "product_id", "product_name", "aspect", "sentiment"])
        .size()
        .reset_index(name="count")
    )
    agg.to_csv(f"{OUT_DIR}/aspect_sentiment.csv", index=False, encoding="utf-8-sig")

    df["brand_name"] = df["brand_name"].fillna("")  # 검색에 브랜드명도 쓰려고 보존 (쿠팡은 브랜드 정보 없음)
    product_summary = (
        df.groupby(["platform", "product_id", "product_name", "category", "brand_name"])
        .agg(review_count=("review_id", "size"), avg_rating=("rating", "mean"))
        .reset_index()
    )
    sentiment_ratio = df.groupby(["platform", "product_id", "sentiment"]).size().unstack(fill_value=0)
    sentiment_ratio.columns = [f"n_{c}" for c in sentiment_ratio.columns]
    sentiment_ratio = sentiment_ratio.reset_index()
    product_summary = product_summary.merge(sentiment_ratio, on=["platform", "product_id"], how="left")
    product_summary.to_csv(f"{OUT_DIR}/product_summary.csv", index=False, encoding="utf-8-sig")

    rep_reviews = (
        df.sort_values("review_id")
        .groupby(["platform", "product_id", "sentiment"])
        .head(3)[["platform", "product_id", "product_name", "sentiment", "rating", "review_content", "nickname"]]
    )
    rep_reviews.to_csv(f"{OUT_DIR}/representative_reviews.csv", index=False, encoding="utf-8-sig")

    with open(f"{OUT_DIR}/absa_filter_stats.txt", "w", encoding="utf-8") as f:
        f.write(str(excluded_count))

    print("저장 완료: aspect_sentiment.csv, product_summary.csv, representative_reviews.csv, absa_filter_stats.txt")
    print(f"상품 수: {len(product_summary)}, 속성 멘션 수: {len(mentions_df)}, 모델이 제외한 리뷰 수: {excluded_count}")


if __name__ == "__main__":
    main()
