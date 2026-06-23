import pandas as pd
import streamlit as st

import report_data as rd

st.set_page_config(page_title="BeautyScope - 화장품 상품 리포트", page_icon="💄", layout="wide")

ASPECTS = ["보습/수분", "향", "트러블/자극", "발림성/흡수력", "지속력", "가격/가성비", "용기/디자인", "효과"]


@st.cache_data
def load_data():
    return rd.load_all()


@st.cache_data
def get_aspect_table(aspect_sentiment, product_summary):
    return rd.build_aspect_table(aspect_sentiment, product_summary)


aspect_sentiment, product_summary, rep_reviews, skin_aspect, skin_summary, reliability = load_data()
aspect_table = get_aspect_table(aspect_sentiment, product_summary)
AVG_RELIABILITY = reliability["reliability_pct"].mean()

st.title("💄 BeautyScope — 화장품 상품 리포트")
st.caption("쿠팡 · 무신사 · 올리브영 538,774건의 리뷰 기반 — 속성별 장단점, 랭킹, 대안 상품까지 한 번에")

tab_report, tab_rank, tab_about = st.tabs(["🛍️ 상품 리포트", "🏆 속성별 랭킹", "ℹ️ 프로젝트 소개"])

# ==================== 상품 리포트 ====================
with tab_report:
    st.subheader("상품을 검색하면 속성별 장단점 · 대안 상품 · 피부타입별 평가를 보여드립니다")

    col_platform, col_cat, col_query = st.columns([1, 1, 2])
    with col_platform:
        platforms = ["전체"] + sorted(product_summary["platform"].dropna().unique().tolist())
        picked_platform = st.selectbox("플랫폼", platforms)
    with col_cat:
        categories = ["전체"] + sorted(product_summary["category"].dropna().unique().tolist())
        picked_category = st.selectbox("카테고리로 좁히기", categories)
    with col_query:
        query = st.text_input(
            "상품명 또는 브랜드로 검색 (여러 단어는 띄어서)",
            placeholder="예: 토너 / 닥터지 / 라로슈포제 시카 / 무신사 보습크림",
        )

    candidates = product_summary.sort_values("review_count", ascending=False)
    if picked_platform != "전체":
        candidates = candidates[candidates["platform"] == picked_platform]
    if picked_category != "전체":
        candidates = candidates[candidates["category"] == picked_category]

    if query.strip():
        # 여러 단어를 입력하면 전부 포함된 상품만 남긴다 (상품명+브랜드명 통째로 검사)
        # 예: "닥터지 토너"를 입력하면 두 단어가 다 들어간 상품만 매칭됨
        search_target = candidates["product_name"].fillna("") + " " + candidates["brand_name"].fillna("")
        search_target = search_target.str.lower()
        keywords = query.lower().split()
        mask = pd.Series(True, index=candidates.index)
        for kw in keywords:
            mask &= search_target.str.contains(kw, regex=False)
        candidates = candidates[mask]

    if candidates.empty:
        st.warning("일치하는 상품이 없습니다. 검색어를 줄이거나 카테고리를 \"전체\"로 바꿔보세요 "
                   "(리뷰 20건 이상인 상품만 리포트를 제공합니다).")
    else:
        st.caption(f"검색 결과 {len(candidates)}개 (리뷰 많은 순)")
        top_candidates = candidates.head(50).reset_index(drop=True)

        def _label(i):
            r = top_candidates.loc[i]
            brand = f"{r['brand_name']} " if r["brand_name"] else ""
            return f"[{r['platform']}] {brand}{r['product_name']} (리뷰 {int(r['review_count']):,}건, 평점 {r['avg_rating']:.1f})"

        selected_idx = st.selectbox(
            f"상품 선택 (상위 {len(top_candidates)}개 표시 — 목록 안에서도 입력해 검색 가능)",
            options=top_candidates.index,
            format_func=_label,
        )
        row = top_candidates.loc[selected_idx]

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("리뷰 수", f"{int(row['review_count']):,}건")
        c2.metric("평균 별점", f"{row['avg_rating']:.2f} / 5")
        pos_ratio = row.get("n_positive", 0) / row["review_count"] * 100
        c3.metric("긍정 비율", f"{pos_ratio:.0f}%")
        neg_ratio = row.get("n_negative", 0) / row["review_count"] * 100
        c4.metric("부정 비율", f"{neg_ratio:.0f}%")

        rel = rd.get_reliability(reliability, row["platform"], row["product_id"])
        if rel is not None:
            c5.metric("리뷰 신뢰도", f"{rel['reliability_pct']:.0f}%",
                      help="학습된 감성분석 모델이 리뷰 텍스트만 보고 판단한 감성이 별점 기반 라벨과 "
                           "얼마나 일치하는지. 낮을수록 별점과 리뷰 내용이 안 맞는 경우가 많다는 뜻")
            if rel["reliability_pct"] < AVG_RELIABILITY - 10:
                st.warning(
                    f"⚠️ 이 상품은 별점과 리뷰 내용이 일치하지 않는 리뷰가 평균보다 많습니다 "
                    f"({rel['mismatch_count']}건 / {rel['review_count']}건). 아래 속성별 분석을 "
                    f"참고할 때 평점만큼 확정적으로 받아들이지 않는 걸 추천합니다."
                )
        else:
            c5.metric("리뷰 신뢰도", "—")

        st.markdown("### 속성별 장단점")
        own_asp = aspect_table[
            (aspect_table["platform"] == row["platform"]) & (aspect_table["product_id"] == row["product_id"])
        ].sort_values("total_mentions", ascending=False)
        if own_asp.empty:
            st.info("이 상품에서는 속성 관련 언급을 충분히 찾지 못했습니다.")
        else:
            for _, r in own_asp.iterrows():
                st.progress(
                    int(r["positive_ratio"]),
                    text=f"**{r['aspect']}** — 긍정 {r['positive_ratio']:.0f}% (언급 {int(r['total_mentions'])}건)",
                )

        st.markdown("### 이거 말고 다른 건? (대안 상품 추천)")
        weakest, alternatives = rd.find_alternatives(aspect_table, row["platform"], row["product_id"])
        if weakest is None:
            st.info("속성 데이터가 충분하지 않아 대안을 추천할 수 없습니다.")
        elif alternatives.empty:
            st.success(f"이 상품의 가장 약한 속성은 **{weakest['aspect']}**(긍정 {weakest['positive_ratio']:.0f}%)이지만, "
                       f"같은 카테고리에서 뚜렷하게 더 나은 대안을 찾지 못했습니다.")
        else:
            st.warning(f"이 상품은 **{weakest['aspect']}** 속성이 가장 약합니다 (긍정 {weakest['positive_ratio']:.0f}%, "
                       f"{int(weakest['total_mentions'])}건 언급). 같은 카테고리에서 이 속성이 더 좋은 상품:")
            for _, alt in alternatives.iterrows():
                st.markdown(
                    f"- **[{alt['platform']}] {alt['product_name']}** — "
                    f"{weakest['aspect']} 긍정 {alt['positive_ratio']:.0f}% "
                    f"(언급 {int(alt['total_mentions'])}건, 평점 {alt['avg_rating']:.1f})"
                )

        st.markdown("### 피부타입별 평가 (무신사 리뷰 기준)")
        skin_result = rd.skin_segment_view(skin_aspect, skin_summary, row["product_id"])
        if skin_result is None:
            st.caption("이 상품은 피부타입 데이터가 없습니다 (무신사에서 수집된 상품만 제공).")
        else:
            pivot, seg_counts = skin_result
            skin_types = sorted(pivot["skin_category"].unique())
            skin_cols = st.columns(len(skin_types))
            for col, skin_type in zip(skin_cols, skin_types):
                with col:
                    n_review = seg_counts[seg_counts["skin_category"] == skin_type]["review_count"]
                    n_review = int(n_review.iloc[0]) if len(n_review) else 0
                    st.markdown(f"**{skin_type} 피부** ({n_review}명)")
                    sub = pivot[pivot["skin_category"] == skin_type].sort_values("total", ascending=False).head(4)
                    for _, r in sub.iterrows():
                        st.caption(f"{r['aspect']}: 긍정 {int(r['positive_ratio'])}%")

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

# ==================== 속성별 랭킹 ====================
with tab_rank:
    st.subheader("카테고리 + 속성을 고르면 그 속성이 가장 좋은 상품 Top 10을 보여드립니다")
    categories = sorted(product_summary["category"].dropna().unique().tolist())

    col1, col2 = st.columns(2)
    with col1:
        rank_category = st.selectbox("카테고리", categories, index=categories.index("토너") if "토너" in categories else 0)
    with col2:
        rank_aspect = st.selectbox("속성", ASPECTS)

    ranking = rd.aspect_ranking(aspect_table, rank_category, rank_aspect, top_n=10)
    if ranking.empty:
        st.info("표본이 충분한 상품이 없습니다 (속성 언급 15건 이상인 상품만 집계).")
    else:
        display = ranking[["platform", "product_name", "positive_ratio", "total_mentions", "avg_rating", "review_count"]].copy()
        display.columns = ["플랫폼", "상품명", "긍정비율(%)", "언급건수", "평균별점", "전체리뷰수"]
        display.insert(0, "순위", range(1, len(display) + 1))
        st.dataframe(display, hide_index=True, use_container_width=True)

# ==================== 프로젝트 소개 ====================
with tab_about:
    st.subheader("프로젝트 개요")
    st.markdown("""
    **BeautyScope**는 쿠팡·무신사·올리브영 3개 플랫폼에서 수집한 화장품 리뷰
    538,774건을 분석해, 구매를 고민하는 사람에게 실제로 쓸모 있는 정보를
    보여주는 서비스입니다.

    - **상품 리포트**: 속성기반 감성분석(ABSA)으로 보습/향/트러블/발림성 등
      8개 속성별 긍정 비율, 약점을 보완하는 대안 상품, 피부타입별(무신사
      기준) 평가, 대표 리뷰까지 한 화면에서 제공
    - **속성별 랭킹**: 카테고리 + 속성을 고르면 그 속성이 가장 좋은 상품
      Top 10을 바로 확인
    - **리뷰 신뢰도**: 학습된 감성분석 모델(TF-IDF+로지스틱회귀, 확률보정
      적용)을 전체 리뷰에 돌려서, 별점 기반 라벨과 모델이 텍스트만 보고
      판단한 감성이 얼마나 일치하는지 상품별로 검증. 별점과 리뷰 내용이
      안 맞는 리뷰가 많은 상품은 속성 분석 결과를 더 신중하게 보도록 안내
    - **데이터**: 쿠팡 86,379건 + 무신사 230,870건 + 올리브영 221,525건
      (중복/노이즈 제거 후 538,774건)

    개발 과정과 문제점/개선 기록은 [DEVLOG.md](./DEVLOG.md)에 정리되어 있습니다.
    """)
