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


# 쿠팡은 20개 키워드로 크롤링해서 category가 바로 세부 카테고리지만, 무신사는
# 원본에 카테고리 컬럼이 없고 올리브영은 4개 대분류(skincare/maskpack/
# cleansing/suncare)뿐이라 product_name 키워드로 쿠팡과 같은 세부 카테고리를
# 추정해서 맞춰준다. 구체적인 키워드를 먼저 검사해야 "선크림"이 "크림"류로
# 잘못 분류되는 걸 막을 수 있어서 순서가 중요하다.
CATEGORY_KEYWORDS = [
    ("선크림", ["선크림", "선스틱", "선쿠션", "자외선차단", "선블록", "선에센스"]),
    ("나이트크림", ["나이트크림"]),
    ("수분크림", ["수분크림", "모이스처크림", "수분 크림"]),
    ("아이크림", ["아이크림"]),
    ("BB크림", ["bb크림", "비비크림"]),
    ("클렌징오일", ["클렌징오일", "클렌징 오일"]),
    ("클렌징폼", ["클렌징폼", "폼클렌징", "클렌징 폼"]),
    ("마스크팩", ["마스크팩", "시트마스크", "마스크 시트"]),
    ("쿠션팩트", ["쿠션", "팩트"]),
    ("파운데이션", ["파운데이션"]),
    ("컨실러", ["컨실러"]),
    ("아이섀도", ["아이섀도", "아이새도"]),
    ("마스카라", ["마스카라"]),
    ("립틴트", ["립틴트", "틴트"]),
    ("립스틱", ["립스틱"]),
    ("토너", ["토너", "스킨토너"]),
    ("세럼", ["세럼", "앰플"]),
    ("미스트", ["미스트"]),
]


def classify_category(product_name, fallback):
    if not isinstance(product_name, str):
        return fallback
    name = product_name.lower()
    for category, keywords in CATEGORY_KEYWORDS:
        if any(kw.lower() in name for kw in keywords):
            return category
    return fallback


# 올리브영의 4개 대분류는 키워드 매칭이 안 될 때 쓸 한글 fallback
_OLIVEYOUNG_FALLBACK = {"skincare": "스킨케어", "maskpack": "마스크팩", "cleansing": "클렌징", "suncare": "선크림"}


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
    df["category"] = df["product_name"].apply(lambda n: classify_category(n, "기타"))
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
                    "category": classify_category(d.get("product_name"), _OLIVEYOUNG_FALLBACK[cat]),
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
