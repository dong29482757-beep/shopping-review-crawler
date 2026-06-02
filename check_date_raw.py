import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 원본에서 날짜 원형 확인
df = pd.read_csv('coupang_reviews_20260514_001626.csv', encoding='utf-8-sig')

print('review_date 샘플 (원본):')
print(df['review_date'].head(20).to_string())
print()
print('타입:', df['review_date'].dtype)
print()
print('고유값 샘플:')
print(df['review_date'].dropna().unique()[:20])
