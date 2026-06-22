import pandas as pd
import streamlit as st
from model_utils import SentimentModels

st.set_page_config(page_title="BeautyScope - 화장품 리뷰 감성 분석", page_icon="💄", layout="wide")

MODEL_DIR = r"D:\crolling\models"


@st.cache_resource
def load_models():
    return SentimentModels(MODEL_DIR)


@st.cache_data
def load_agg(name):
    return pd.read_csv(f"{MODEL_DIR}/{name}", encoding="utf-8-sig")


st.title("💄 BeautyScope — 화장품 리뷰 감성 분석")
st.caption("쿠팡 · 무신사 · 올리브영 538,774건의 화장품 리뷰를 학습한 감성 분류 서비스")

tab1, tab2, tab3 = st.tabs(["🔍 리뷰 감성 분석 데모", "📊 데이터 대시보드", "ℹ️ 프로젝트 소개"])

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

        st.caption(f"전처리된 텍스트: {result['cleaned_text']}")

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
        st.subheader("부정 리뷰 다빈도 단어 Top 30")
        st.dataframe(load_agg("agg_top_negative_words.csv"), hide_index=True, use_container_width=True, height=400)
    with col2:
        st.subheader("긍정 리뷰 다빈도 단어 Top 30")
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
    538,774건을 학습해 리뷰의 감성(긍정/중립/부정)을 분류하는 서비스입니다.

    - **ML 모델**: TF-IDF + LogisticRegression — accuracy 0.738, macro F1 0.677
    - **DL 모델**: numpy로 직접 구현한 3층 피드포워드 신경망 — accuracy 0.762, macro F1 0.663
    - **데이터**: 쿠팡 86,379건 + 무신사 230,870건 + 올리브영 221,525건 (중복/노이즈 제거 후 538,774건)

    개발 과정에서 겪은 문제와 해결 방법은 [DEVLOG.md](./DEVLOG.md)에 정리되어 있습니다.
    """)
