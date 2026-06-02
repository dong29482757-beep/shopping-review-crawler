import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv('coupang_reviews_final.csv', encoding='utf-8-sig', keep_default_na=False)

print('=== 컬럼별 타입 및 예시값 ===')
for col in df.columns:
    sample = df[col].iloc[0]
    print(f'{col} ({df[col].dtype}): {repr(str(sample)[:60])}')

print()
print('=== 샘플 1건 전체 ===')
row = df[df['sentiment'] == 'negative'].iloc[0]
for col in df.columns:
    print(f'  {col}: {str(row[col])[:80]}')
