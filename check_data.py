import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv('coupang_reviews_ALL.csv', encoding='utf-8-sig')

print('=== 기본 정보 ===')
print(f'총 행: {len(df):,}건')
print(f'컬럼: {list(df.columns)}')
print()

print('=== 결측값 ===')
print(df.isnull().sum())
print()

print('=== 중복 (review_id 기준) ===')
dup = df.duplicated(subset=['review_id']).sum()
print(f'중복 건수: {dup:,}건')
print()

print('=== 샘플 (review_content 앞 50자) ===')
for _, row in df.head(3).iterrows():
    print(f"  keyword={row['keyword']}, rating={row['rating']}, content={str(row['review_content'])[:50]}")
print()

print('=== keyword 분포 (상위 20개) ===')
print(df['keyword'].value_counts().head(20))

print()
print('=== rating 분포 ===')
print(df['rating'].value_counts().sort_index())
