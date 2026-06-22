"""
피부타입별 속성 분석 (무신사 원본 데이터 활용).

merge_datasets.py로 통합할 때 컬럼 스키마를 통일하면서 무신사 원본의
skin_type(피부타입) 정보를 버렸었다. 하지만 이 정보가 있으면 "건성 피부
리뷰어들은 이 토너의 보습력을 어떻게 평가하나" 같은, 평균 평점만으로는
안 보이는 세그먼트별 정보를 만들 수 있어서 원본에서 다시 추출한다.

무신사 raw skin_type 컬럼은 "복합성 · 유수분조절 · 모공 · 여드름" 형태로
피부타입과 피부고민이 섞여 있다 — 맨 앞 토큰이 피부타입이다.
올리브영은 skin_type이 대부분 null이라 (skin_concern만 있음) 이 분석에서는
무신사만 사용한다.
"""
import time
import pandas as pd

from absa import extract_aspect_sentiments

SRC = r"C:\Users\user\Desktop\데이터\musinsa_beauty_TOTAL.csv"
OUT_DIR = r"D:\crolling\models"

VALID_SKIN_TYPES = {"복합성", "지성", "건성", "민감성"}
MIN_REVIEWS_PER_SEGMENT = 10


def rating_to_sentiment(r):
    if pd.isna(r):
        return None
    if r >= 4:
        return "positive"
    if r == 3:
        return "neutral"
    return "negative"


def parse_skin_type(raw):
    if not isinstance(raw, str) or not raw.strip():
        return None
    first = raw.split("·")[0].strip()
    return first if first in VALID_SKIN_TYPES else None


def main():
    print("로딩...")
    df = pd.read_csv(SRC, encoding="utf-8-sig", low_memory=False)
    df["skin_category"] = df["skin_type"].apply(parse_skin_type)
    df = df.dropna(subset=["skin_category", "review_text", "rating"])
    df["sentiment"] = df["rating"].apply(rating_to_sentiment)
    df = df[df["review_text"].str.strip().str.len() >= 5]
    print(f"피부타입 식별된 리뷰: {len(df)}건")
    print(df["skin_category"].value_counts())

    review_counts = df.groupby(["product_id", "skin_category"]).size()
    valid = set(review_counts[review_counts >= MIN_REVIEWS_PER_SEGMENT].index)
    df["seg_key"] = list(zip(df["product_id"], df["skin_category"]))
    df = df[df["seg_key"].isin(valid)]
    print(f"세그먼트(상품x피부타입) 최소 {MIN_REVIEWS_PER_SEGMENT}건 이상 리뷰: {len(valid)}개, 대상 리뷰 {len(df)}건")

    t0 = time.time()
    rows = []
    for _, row in df.iterrows():
        mentions = extract_aspect_sentiments(row["review_text"], fallback_sentiment=row["sentiment"])
        for aspect, sentiment in mentions:
            rows.append((row["product_id"], row["product_name"], row["skin_category"], aspect, sentiment))
    print(f"속성 추출 완료: {time.time()-t0:.1f}s, mentions={len(rows)}")

    mentions_df = pd.DataFrame(
        rows, columns=["product_id", "product_name", "skin_category", "aspect", "sentiment"]
    )
    agg = (
        mentions_df.groupby(["product_id", "product_name", "skin_category", "aspect", "sentiment"])
        .size()
        .reset_index(name="count")
    )
    agg.to_csv(f"{OUT_DIR}/skin_aspect_sentiment.csv", index=False, encoding="utf-8-sig")

    seg_summary = (
        df.groupby(["product_id", "product_name", "skin_category"])
        .agg(review_count=("rating", "size"), avg_rating=("rating", "mean"))
        .reset_index()
    )
    seg_summary.to_csv(f"{OUT_DIR}/skin_segment_summary.csv", index=False, encoding="utf-8-sig")

    print("저장 완료: skin_aspect_sentiment.csv, skin_segment_summary.csv")
    print(f"상품x피부타입 세그먼트 수: {len(seg_summary)}, 속성 멘션 수: {len(mentions_df)}")


if __name__ == "__main__":
    main()
