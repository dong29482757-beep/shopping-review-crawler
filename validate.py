import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv('coupang_reviews_final.csv', encoding='utf-8-sig', keep_default_na=False)

print('=== 1. 기본 현황 ===')
print(f'총 건수: {len(df):,}')
print(f'컬럼: {list(df.columns)}')
print()

print('=== 2. 날짜 분포 (연도별) ===')
df['year'] = df['review_date'].str[:4]
print(df['year'].value_counts().sort_index().to_string())
print()

print('=== 3. 감성 레이블 vs 평점 교차 확인 ===')
print(pd.crosstab(df['rating'], df['sentiment']).to_string())
print()

print('=== 4. 텍스트 길이 통계 ===')
df['content_len'] = df['review_content'].str.len()
print(f'  최소: {df["content_len"].min()}자')
print(f'  최대: {df["content_len"].max()}자')
print(f'  평균: {df["content_len"].mean():.1f}자')
print(f'  10자 미만: {(df["content_len"] < 10).sum()}건')
print()

print('=== 5. review_title 현황 ===')
print(f'  빈 문자열: {(df["review_title"] == "").sum():,}건')
print(f'  내용 있는 것: {(df["review_title"] != "").sum():,}건')
print()

print('=== 6. 키워드별 건수 ===')
print(df['keyword'].value_counts().to_string())
print()

print('=== 7. 샘플 리뷰 (각 감성별 1건씩) ===')
for sentiment in ['positive', 'negative', 'neutral']:
    row = df[df['sentiment'] == sentiment].iloc[0]
    print(f'\n[{sentiment}] rating={row["rating"]}, keyword={row["keyword"]}, date={row["review_date"]}')
    print(f'  제목: {row["review_title"][:50] if row["review_title"] else "(없음)"}')
    print(f'  본문: {row["review_content"][:80]}')
