"""
테스트 실행 - 화장품 키워드, 상품 1개, 리뷰 30건
실행 전: Chrome 완전히 닫기!
"""
from coupang_crawler import CoupangCrawler

with CoupangCrawler(headless=False) as crawler:
    df = crawler.run(keyword="화장품", max_products=1, max_reviews=30, min_negative=5)
    crawler.summary(df)
    if not df.empty:
        print(df[["rating", "review_date", "review_content"]].head(10).to_string())
    else:
        print("리뷰 0건 - 수집 실패")
    crawler.save(df)
