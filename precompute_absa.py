"""
538,774건 전체 리뷰에 속성기반 감성분석을 적용해 상품별 집계를 만든다.
규칙 기반(absa.py)이라 Okt 형태소분석 없이 정규식만으로 처리 가능해서
전체 데이터에 적용해도 수십 초 내에 끝난다.
"""
import time
import collections
import pandas as pd

from absa import extract_aspect_sentiments

SRC = r"D:\crolling\merged_reviews_all.csv"
OUT_DIR = r"D:\crolling\models"

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

    print("저장 완료: aspect_sentiment.csv, product_summary.csv, representative_reviews.csv")
    print(f"상품 수: {len(product_summary)}, 속성 멘션 수: {len(mentions_df)}")


if __name__ == "__main__":
    main()
