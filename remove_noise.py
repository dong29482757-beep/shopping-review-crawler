import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv('coupang_reviews_final.csv', encoding='utf-8-sig', keep_default_na=False)
print(f'제거 전: {len(df):,}건')

# 체험단/협찬 리뷰 제거
ad_pattern = '협찬|체험단|제공받|무상으로|무료로 받|리뷰어'
before = len(df)
df = df[~df['review_content'].str.contains(ad_pattern, na=False)]
print(f'체험단 제거 후: {len(df):,}건 (제거: {before - len(df):,}건)')

# 도배 리뷰 제거 (앞 50자 기준 중복)
before = len(df)
df['content_prefix'] = df['review_content'].str[:50]
df = df.drop_duplicates(subset=['content_prefix'])
df = df.drop(columns=['content_prefix'])
print(f'도배 제거 후: {len(df):,}건 (제거: {before - len(df):,}건)')

# 저장
df.to_csv('coupang_reviews_final.csv', index=False, encoding='utf-8-sig', na_rep='')
print(f'\n최종 저장 완료: {len(df):,}건')

print('\n=== 최종 현황 ===')
print(f'키워드 수: {df["keyword"].nunique()}개')
print(f'상품 수: {df["product_id"].nunique():,}개')
print(f'기간: {df["review_date"].min()} ~ {df["review_date"].max()}')
print(f'\n감성 분포:')
print(df['sentiment'].value_counts().to_string())
print(f'\n키워드별 건수:')
print(df['keyword'].value_counts().to_string())
