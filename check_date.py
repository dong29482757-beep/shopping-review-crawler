import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv('coupang_reviews_final.csv', encoding='utf-8-sig')

bad = df[df['review_date'] == '1970-01-01']
print(f'1970-01-01 건수: {len(bad)}건')
print()
print('샘플:')
for _, row in bad.head(5).iterrows():
    print(f"  review_id={row['review_id']}, keyword={row['keyword']}, date={row['review_date']}, content={str(row['review_content'])[:40]}")
