"""
상품 리포트 화면에서 쓰는 데이터 가공 로직 — 랭킹 / 대안추천 / 피부타입 세그먼트.

전부 precompute_absa.py / precompute_skin_segments.py가 미리 만들어둔 집계
CSV만 읽어서 계산한다 (요청마다 538,774건을 다시 훑지 않음).
"""
import pandas as pd

MODEL_DIR = r"D:\crolling\models"
MIN_MENTIONS = 15  # 이 미만이면 랭킹/대안 후보에서 제외 (표본이 적어 신뢰도 낮음)
MIN_SKIN_REVIEWS = 10


def load_all(model_dir=MODEL_DIR):
    aspect_sentiment = pd.read_csv(f"{model_dir}/aspect_sentiment.csv", encoding="utf-8-sig")
    product_summary = pd.read_csv(f"{model_dir}/product_summary.csv", encoding="utf-8-sig")
    rep_reviews = pd.read_csv(f"{model_dir}/representative_reviews.csv", encoding="utf-8-sig")
    skin_aspect = pd.read_csv(f"{model_dir}/skin_aspect_sentiment.csv", encoding="utf-8-sig")
    skin_summary = pd.read_csv(f"{model_dir}/skin_segment_summary.csv", encoding="utf-8-sig")
    reliability = pd.read_csv(f"{model_dir}/review_reliability.csv", encoding="utf-8-sig")
    return aspect_sentiment, product_summary, rep_reviews, skin_aspect, skin_summary, reliability


def get_reliability(reliability, platform, product_id):
    """학습된 모델이 텍스트만 보고 판단한 감성과 별점 기반 라벨이 얼마나
    일치하는지(=리뷰 신뢰도) 상품 단위로 조회. 모델을 평가용으로만 두지 않고
    서비스 품질 검증에 실제로 활용하는 지표."""
    row = reliability[(reliability["platform"] == platform) & (reliability["product_id"] == product_id)]
    if row.empty:
        return None
    return row.iloc[0]


def build_aspect_table(aspect_sentiment, product_summary):
    """(platform, product_id, aspect)별 총 멘션수/긍정비율 + category 붙인 테이블."""
    pivot = aspect_sentiment.pivot_table(
        index=["platform", "product_id", "aspect"], columns="sentiment", values="count", fill_value=0
    ).reset_index()
    for col in ["positive", "negative", "neutral"]:
        if col not in pivot.columns:
            pivot[col] = 0
    pivot["total_mentions"] = pivot["positive"] + pivot["negative"] + pivot["neutral"]
    pivot["positive_ratio"] = (pivot["positive"] / pivot["total_mentions"] * 100).round(1)

    meta = product_summary[["platform", "product_id", "product_name", "category", "review_count", "avg_rating"]]
    return pivot.merge(meta, on=["platform", "product_id"], how="left")


def aspect_ranking(aspect_table, category, aspect, top_n=10, ascending=False):
    """카테고리+속성 기준 Top N 랭킹 (ascending=True면 약점 랭킹)."""
    subset = aspect_table[
        (aspect_table["category"] == category)
        & (aspect_table["aspect"] == aspect)
        & (aspect_table["total_mentions"] >= MIN_MENTIONS)
    ]
    return subset.sort_values("positive_ratio", ascending=ascending).head(top_n)


def find_alternatives(aspect_table, platform, product_id, top_n=5, min_margin=10.0):
    """선택한 상품의 약점 속성을 찾고, 같은 카테고리에서 그 속성이 더 나은 대안 상품을 추천.

    절대 임계값(예: 긍정비율 80% 이상) 대신 "현재 상품보다 충분히 나은가"로
    판단한다 — 속성마다 긍정비율의 기본 수준이 다르기 때문 (예: 트러블/자극은
    애초에 언급될 때 대부분 불만 맥락이라 카테고리 전체 평균이 낮음).
    """
    own = aspect_table[(aspect_table["platform"] == platform) & (aspect_table["product_id"] == product_id)]
    own_reliable = own[own["total_mentions"] >= MIN_MENTIONS]
    if own_reliable.empty:
        return None, pd.DataFrame()

    weakest = own_reliable.sort_values("positive_ratio").iloc[0]
    category = weakest["category"]

    candidates = aspect_table[
        (aspect_table["category"] == category)
        & (aspect_table["aspect"] == weakest["aspect"])
        & (aspect_table["total_mentions"] >= MIN_MENTIONS)
        & (aspect_table["positive_ratio"] >= weakest["positive_ratio"] + min_margin)
        & ~((aspect_table["platform"] == platform) & (aspect_table["product_id"] == product_id))
    ]
    candidates = candidates.sort_values("positive_ratio", ascending=False).head(top_n)
    return weakest, candidates


def skin_segment_view(skin_aspect, skin_summary, product_id):
    """무신사 상품에 대해서만 피부타입별(건성/지성/복합성/민감성) 속성 긍정비율 제공."""
    asp = skin_aspect[skin_aspect["product_id"] == product_id]
    if asp.empty:
        return None
    pivot = asp.pivot_table(
        index=["skin_category", "aspect"], columns="sentiment", values="count", fill_value=0
    ).reset_index()
    for col in ["positive", "negative", "neutral"]:
        if col not in pivot.columns:
            pivot[col] = 0
    pivot["total"] = pivot["positive"] + pivot["negative"] + pivot["neutral"]
    pivot["positive_ratio"] = (pivot["positive"] / pivot["total"] * 100).round(0)
    seg_counts = skin_summary[skin_summary["product_id"] == product_id]
    return pivot, seg_counts
