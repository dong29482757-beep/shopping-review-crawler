"""
대시보드에서 538,774건 원본 CSV를 매번 읽으면 Streamlit이 느려져서
미리 집계해둔 작은 파일들을 만들어둔다 (플랫폼별/월별/키워드별 통계).
"""
import collections
import pandas as pd

from preprocessing_ko import tokenize

SRC = r"D:\crolling\merged_reviews_all.csv"
OUT_DIR = r"D:\crolling\models"


def main():
    print("로딩...")
    df = pd.read_csv(SRC, low_memory=False)
    df["review_date"] = pd.to_datetime(df["review_date"], errors="coerce")
    df["year_month"] = df["review_date"].dt.to_period("M").astype(str)

    platform_counts = df["platform"].value_counts().reset_index()
    platform_counts.columns = ["platform", "count"]
    platform_counts.to_csv(f"{OUT_DIR}/agg_platform_counts.csv", index=False, encoding="utf-8-sig")

    rating_dist = df.groupby(["platform", "rating"]).size().reset_index(name="count")
    rating_dist.to_csv(f"{OUT_DIR}/agg_rating_dist.csv", index=False, encoding="utf-8-sig")

    sentiment_dist = df.groupby(["platform", "sentiment"]).size().reset_index(name="count")
    sentiment_dist.to_csv(f"{OUT_DIR}/agg_sentiment_dist.csv", index=False, encoding="utf-8-sig")

    monthly = df[df["year_month"].notna() & (df["year_month"] != "NaT")]
    monthly = monthly.groupby(["year_month", "platform"]).size().reset_index(name="count")
    monthly = monthly[monthly["year_month"] >= "2022-01"]
    monthly.to_csv(f"{OUT_DIR}/agg_monthly_trend.csv", index=False, encoding="utf-8-sig")

    category_sentiment = df.groupby(["category", "sentiment"]).size().reset_index(name="count")
    category_sentiment.to_csv(f"{OUT_DIR}/agg_category_sentiment.csv", index=False, encoding="utf-8-sig")

    print("부정 리뷰 키워드 집계...")
    neg = df[df["sentiment"] == "negative"]
    counter = collections.Counter()
    for text in neg["review_content"].dropna():
        counter.update(tokenize(text))
    top_neg_words = pd.DataFrame(counter.most_common(30), columns=["word", "count"])
    top_neg_words.to_csv(f"{OUT_DIR}/agg_top_negative_words.csv", index=False, encoding="utf-8-sig")

    print("긍정 리뷰 키워드 집계...")
    pos = df[df["sentiment"] == "positive"].sample(n=min(20000, (df["sentiment"] == "positive").sum()), random_state=42)
    counter2 = collections.Counter()
    for text in pos["review_content"].dropna():
        counter2.update(tokenize(text))
    top_pos_words = pd.DataFrame(counter2.most_common(30), columns=["word", "count"])
    top_pos_words.to_csv(f"{OUT_DIR}/agg_top_positive_words.csv", index=False, encoding="utf-8-sig")

    sample = df.sample(n=2000, random_state=42)[
        ["platform", "category", "product_name", "rating", "sentiment", "review_content", "review_date"]
    ]
    sample.to_csv(f"{OUT_DIR}/sample_reviews.csv", index=False, encoding="utf-8-sig")

    print("완료. 전체 건수:", len(df))


if __name__ == "__main__":
    main()
