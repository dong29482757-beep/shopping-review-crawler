import pandas as pd
import streamlit as st
from model_utils import SentimentModels

st.set_page_config(page_title="BeautyScope - 화장품 리뷰 분석", page_icon="💄", layout="wide")

MODEL_DIR = r"D:\crolling\models"
ASPECTS = ["보습/수분", "향", "트러블/자극", "발림성/흡수력", "지속력", "가격/가성비", "용기/디자인", "효과"]


@st.cache_resource
def load_models():
    return SentimentModels(MODEL_DIR)


@st.cache_data
def load_agg(name):
    return pd.read_csv(f"{MODEL_DIR}/{name}", encoding="utf-8-sig")


st.title("💄 BeautyScope — 화장품 리뷰 분석")
st.caption("쿠팡 · 무신사 · 올리브영 538,774건의 화장품 리뷰 기반 — 살까 말까 고민될 때 속성별로 장단점을 확인하세요")

tab0, tab1, tab2, tab3 = st.tabs(["🛍️ 상품 리포트", "🔍 리뷰 텍스트 분석", "📊 데이터 대시보드", "ℹ️ 프로젝트 소개"])

# ---------------- 상품 리포트 (핵심 기능) ----------------
with tab0:
    st.subheader("상품을 검색하면 속성별 장단점과 대표 리뷰를 보여드립니다")
    product_summary = load_agg("product_summary.csv")
    aspect_sentiment = load_agg("aspect_sentiment.csv")
    rep_reviews = load_agg("representative_reviews.csv")

    product_summary = product_summary.sort_values("review_count", ascending=False)
    query = st.text_input("상품명 검색", placeholder="예: 토너, 선크림, 닥터지, 라로슈포제 ...")

    candidates = product_summary
    if query.strip():
        candidates = product_summary[product_summary["product_name"].str.contains(query, case=False, na=False)]

    if candidates.empty:
        st.warning("일치하는 상품이 없습니다. 리뷰 20건 이상인 상품만 리포트를 제공합니다.")
    else:
        options = candidates.head(50).apply(
            lambda r: f"[{r['platform']}] {r['product_name']} (리뷰 {int(r['review_count'])}건, 평점 {r['avg_rating']:.1f})",
            axis=1,
        ).tolist()
        selected = st.selectbox(f"상품 선택 ({len(candidates)}개 중 상위 50개 표시)", options)
        row = candidates.iloc[options.index(selected)]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("리뷰 수", f"{int(row['review_count']):,}건")
        c2.metric("평균 별점", f"{row['avg_rating']:.2f} / 5")
        pos_ratio = row.get("n_positive", 0) / row["review_count"] * 100
        c3.metric("긍정 비율", f"{pos_ratio:.0f}%")
        neg_ratio = row.get("n_negative", 0) / row["review_count"] * 100
        c4.metric("부정 비율", f"{neg_ratio:.0f}%")

        st.markdown("### 속성별 장단점")
        asp = aspect_sentiment[
            (aspect_sentiment["platform"] == row["platform"]) & (aspect_sentiment["product_id"] == row["product_id"])
        ]
        if asp.empty:
            st.info("이 상품에서는 속성 관련 언급을 충분히 찾지 못했습니다.")
        else:
            pivot = asp.pivot_table(index="aspect", columns="sentiment", values="count", fill_value=0)
            for col in ["positive", "negative", "neutral"]:
                if col not in pivot.columns:
                    pivot[col] = 0
            pivot["총 언급"] = pivot["positive"] + pivot["negative"] + pivot["neutral"]
            pivot["긍정 비율(%)"] = (pivot["positive"] / pivot["총 언급"] * 100).round(0)
            pivot = pivot.sort_values("총 언급", ascending=False)

            for aspect_name, r in pivot.iterrows():
                bar_col, label_col = st.columns([5, 1])
                with bar_col:
                    st.progress(int(r["긍정 비율(%)"]), text=f"**{aspect_name}** — 긍정 {int(r['긍정 비율(%)'])}% (언급 {int(r['총 언급'])}건)")

        st.markdown("### 대표 리뷰")
        product_reviews = rep_reviews[
            (rep_reviews["platform"] == row["platform"]) & (rep_reviews["product_id"] == row["product_id"])
        ]
        col_pos, col_neg = st.columns(2)
        with col_pos:
            st.markdown("**👍 긍정 리뷰**")
            for _, r in product_reviews[product_reviews["sentiment"] == "positive"].head(3).iterrows():
                st.success(f"★{r['rating']:.0f} {r['review_content'][:150]}")
        with col_neg:
            st.markdown("**👎 부정 리뷰**")
            neg_reviews = product_reviews[product_reviews["sentiment"] == "negative"].head(3)
            if neg_reviews.empty:
                st.info("부정 리뷰가 거의 없습니다.")
            for _, r in neg_reviews.iterrows():
                st.error(f"★{r['rating']:.0f} {r['review_content'][:150]}")

        st.caption("속성별 긍정 비율은 규칙 기반 속성분석(absa.py)으로 산출 — 리뷰를 문장 단위로 나눠 속성 키워드와 감성 단어를 매칭합니다.")

# ---------------- 리뷰 텍스트 분석 (보조 기능) ----------------
with tab1:
    st.subheader("리뷰 텍스트를 입력하면 ML / DL 두 모델이 동시에 예측합니다")
    sample_texts = [
        "직접 입력하기",
        "촉촉하고 흡수도 잘 되고 향도 좋아요 재구매 의사 있습니다",
        "발림성은 좋은데 향이 너무 강하고 트러블이 났어요 비추천합니다",
        "그냥 무난해요 딱히 좋지도 나쁘지도 않은 평범한 제품",
    ]
    choice = st.selectbox("예시 리뷰 선택", sample_texts)
    default_text = "" if choice == sample_texts[0] else choice
    text = st.text_area("리뷰 내용", value=default_text, height=120,
                         placeholder="예: 피부가 좋아지고 촉촉해서 만족스러워요")

    if st.button("감성 분석 실행", type="primary") and text.strip():
        models = load_models()
        result = models.predict(text)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🤖 ML (TF-IDF + LogisticRegression)")
            st.metric("예측 감성", result["ml"]["label_ko"])
            st.bar_chart(pd.Series(result["ml"]["proba"]))
        with col2:
            st.markdown("### 🧠 DL (numpy 직접 구현 신경망)")
            st.metric("예측 감성", result["dl"]["label_ko"])
            st.bar_chart(pd.Series(result["dl"]["proba"]))

        st.caption(f"형태소 분석 후 토큰: {result['cleaned_text']}")

with tab2:
    st.subheader("플랫폼별 리뷰 현황")
    platform_counts = load_agg("agg_platform_counts.csv")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.dataframe(platform_counts, hide_index=True, use_container_width=True)
    with c2:
        st.bar_chart(platform_counts.set_index("platform")["count"])

    st.subheader("플랫폼별 별점 분포")
    rating_dist = load_agg("agg_rating_dist.csv")
    pivot = rating_dist.pivot(index="rating", columns="platform", values="count").fillna(0)
    st.bar_chart(pivot)

    st.subheader("월별 리뷰 추이 (2022년 이후)")
    monthly = load_agg("agg_monthly_trend.csv")
    monthly_pivot = monthly.pivot(index="year_month", columns="platform", values="count").fillna(0)
    st.line_chart(monthly_pivot)

    st.subheader("카테고리별 감성 분포")
    cat_sent = load_agg("agg_category_sentiment.csv")
    cat_pivot = cat_sent.pivot(index="category", columns="sentiment", values="count").fillna(0)
    st.bar_chart(cat_pivot)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("부정 리뷰 다빈도 단어 Top 30 (형태소 분석 기반)")
        st.dataframe(load_agg("agg_top_negative_words.csv"), hide_index=True, use_container_width=True, height=400)
    with col2:
        st.subheader("긍정 리뷰 다빈도 단어 Top 30 (형태소 분석 기반)")
        st.dataframe(load_agg("agg_top_positive_words.csv"), hide_index=True, use_container_width=True, height=400)

    st.subheader("리뷰 샘플 둘러보기")
    sample = load_agg("sample_reviews.csv")
    platform_filter = st.multiselect("플랫폼 필터", sample["platform"].unique().tolist(),
                                      default=sample["platform"].unique().tolist())
    st.dataframe(sample[sample["platform"].isin(platform_filter)], use_container_width=True, height=300)

with tab3:
    st.subheader("프로젝트 개요")
    st.markdown("""
    **BeautyScope**는 쿠팡·무신사·올리브영 3개 플랫폼에서 수집한 화장품 리뷰
    538,774건을 분석하는 서비스입니다.

    - **상품 리포트**: 속성기반 감성분석(ABSA)으로 보습/향/트러블/발림성 등
      8개 속성별 긍정 비율과 대표 리뷰를 보여줘 구매 의사결정을 돕습니다
    - **리뷰 텍스트 분석**: 형태소 분석(Okt) 기반 TF-IDF로 학습한 ML/DL
      감성 분류 모델 두 가지를 비교해서 보여줍니다
    - **데이터**: 쿠팡 86,379건 + 무신사 230,870건 + 올리브영 221,525건
      (중복/노이즈 제거 후 538,774건)

    개발 과정과 문제점/개선 기록은 [DEVLOG.md](./DEVLOG.md)에 정리되어 있습니다.
    """)
