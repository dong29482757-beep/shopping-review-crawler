"""
쿠팡 + 무신사 + 올리브영 화장품 리뷰 통합 스크립트.

각 플랫폼마다 컬럼명/라벨링 기준이 달라서 그대로 합치면 학습에 쓸 수 없다.
통일 기준: sentiment는 항상 rating에서 재계산한다 (4~5=positive, 3=neutral, 1~2=negative).
무신사 원본 sentiment(텍스트 분석 기반)는 sentiment_text_raw로 보존만 한다.
"""
import json
import pandas as pd

DATA_DIR = r"C:\Users\user\Desktop\데이터"

UNIFIED_COLS = [
    "platform", "review_id", "product_id", "product_name", "brand_name",
    "category", "rating", "sentiment", "sentiment_text_raw",
    "review_title", "review_content", "review_date", "nickname",
]


def rating_to_sentiment(r):
    if pd.isna(r):
        return None
    if r >= 4:
        return "positive"
    if r == 3:
        return "neutral"
    return "negative"


def load_coupang():
    df = pd.read_csv(r"D:\crolling\coupang_reviews_final.csv")
    df["platform"] = "coupang"
    df["brand_name"] = None
    df["category"] = df["keyword"]
    df["sentiment_text_raw"] = None
    df["sentiment"] = df["rating"].apply(rating_to_sentiment)
    return df[UNIFIED_COLS]


def load_musinsa():
    df = pd.read_csv(f"{DATA_DIR}\\musinsa_beauty_TOTAL.csv", encoding="utf-8-sig", low_memory=False)
    df["platform"] = "musinsa"
    df["review_id"] = None
    df["category"] = None
    df["review_title"] = None
    df["sentiment_text_raw"] = df["sentiment"]
    df["sentiment"] = df["rating"].apply(rating_to_sentiment)
    df = df.rename(columns={"review_text": "review_content", "date": "review_date"})
    return df[UNIFIED_COLS]


def load_oliveyoung():
    files = {
        "cleansing": "cleansing_reviews.jsonl",
        "maskpack": "maskpack_reviews.jsonl",
        "skincare": "skincare_reviews.jsonl",
        "suncare": "suncare_reviews.jsonl",
    }
    rows = []
    for cat, fn in files.items():
        with open(f"{DATA_DIR}\\oliveyoung\\{fn}", encoding="utf-8") as f:
            for line in f:
                d = json.loads(line)
                rows.append({
                    "platform": "oliveyoung",
                    "review_id": d.get("review_id"),
                    "product_id": d.get("product_id"),
                    "product_name": d.get("product_name"),
                    "brand_name": d.get("brand"),
                    "category": cat,
                    "rating": d.get("rating"),
                    "sentiment_text_raw": None,
                    "review_title": None,
                    "review_content": d.get("review_text"),
                    "review_date": d.get("review_date"),
                    "nickname": None,
                })
    df = pd.DataFrame(rows)
    df["sentiment"] = df["rating"].apply(rating_to_sentiment)
    return df[UNIFIED_COLS]


def main():
    print("쿠팡 로딩...")
    coupang = load_coupang()
    print(f"  {len(coupang):,}건")

    print("무신사 로딩...")
    musinsa = load_musinsa()
    print(f"  {len(musinsa):,}건")

    print("올리브영 로딩...")
    oliveyoung = load_oliveyoung()
    print(f"  {len(oliveyoung):,}건")

    merged = pd.concat([coupang, musinsa, oliveyoung], ignore_index=True)

    before = len(merged)
    merged = merged.dropna(subset=["review_content", "rating"])
    merged = merged[merged["review_content"].str.strip().str.len() > 0]
    merged = merged.drop_duplicates(subset=["platform", "product_id", "nickname", "review_date", "review_content"])
    after = len(merged)
    print(f"클리닝: {before:,} -> {after:,} ({before - after:,}건 제거)")

    out_path = r"D:\crolling\merged_reviews_all.csv"
    merged.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"저장 완료: {out_path}")

    print("\n=== 플랫폼별 건수 ===")
    print(merged["platform"].value_counts())
    print("\n=== 전체 sentiment 분포 ===")
    print(merged["sentiment"].value_counts())
    print("\n=== 플랫폼별 rating 분포 ===")
    print(pd.crosstab(merged["platform"], merged["rating"]))


if __name__ == "__main__":
    main()
