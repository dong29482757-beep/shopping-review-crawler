"""
추가 수집 - 기존 CSV와 중복 없이 새 키워드로 수집
실행 전: Chrome 완전히 닫기!
"""
import glob
import pandas as pd
from coupang_crawler import CoupangCrawler

# 기존 수집 데이터에서 이미 수집한 product_id 로드
existing_files = glob.glob("coupang_reviews_*.csv")
if existing_files:
    existing_df = pd.concat([pd.read_csv(f) for f in existing_files], ignore_index=True)
    seen_product_ids = set(existing_df["product_id"].astype(str).unique())
    print(f"기존 수집 상품 {len(seen_product_ids)}개 제외 예정")
else:
    seen_product_ids = set()
    print("기존 데이터 없음")

NEW_KEYWORDS = [
    "BB크림",
    "쿠션팩트",
    "컨실러",
    "수분크림",
    "클렌징오일",
    "립틴트",
    "아이섀도",
    "마스카라",
    "나이트크림",
    "미스트",
]


class CoupangCrawlerFiltered(CoupangCrawler):
    def __init__(self, skip_product_ids, **kwargs):
        super().__init__(**kwargs)
        self._skip_ids = skip_product_ids

    def get_product_list(self, keyword, max_products=50):
        all_products = super().get_product_list(keyword, max_products * 2)
        filtered = [p for p in all_products if str(p["product_id"]) not in self._skip_ids]
        print(f"  → 중복 제외 후 {len(filtered)}개 (전체 {len(all_products)}개)")
        return filtered[:max_products]


with CoupangCrawlerFiltered(skip_product_ids=seen_product_ids, headless=False) as crawler:
    df = crawler.run_multi_keyword(
        keywords=NEW_KEYWORDS,
        max_products=30,
        max_reviews=300,
        min_negative=30,
    )
    crawler.summary(df)
    crawler.save(df)
