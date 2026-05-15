"""
본격 수집 - 화장품 카테고리 10개 키워드, 상품 30개, 리뷰 300건
예상 수집량: 50,000~60,000건 / 예상 소요시간: 14~16시간
실행 전: Chrome 완전히 닫기!
"""
from coupang_crawler import CoupangCrawler

KEYWORDS = [
    "화장품",
    "스킨케어",
    "마스크팩",
    "선크림",
    "토너",
    "세럼",
    "클렌징폼",
    "파운데이션",
    "립스틱",
    "아이크림",
]

with CoupangCrawler(headless=False) as crawler:
    df = crawler.run_multi_keyword(
        keywords=KEYWORDS,
        max_products=30,
        max_reviews=300,
        min_negative=30,
    )
    crawler.summary(df)
    crawler.save(df)
