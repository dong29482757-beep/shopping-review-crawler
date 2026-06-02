import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv('coupang_reviews_final.csv', encoding='utf-8-sig', keep_default_na=False)

# ================================================================
# [2번] 정확성 - 평점 vs 내용 모순 체크
# ================================================================
print('=== [2번] 평점-내용 모순 체크 ===\n')

# 5점인데 부정 키워드 포함
negative_keywords = ['별로', '실망', '환불', '불량', '최악', '후회', '쓰레기', '불편', '냄새', '이상해', '이상한', '안좋', '안 좋']
pattern = '|'.join(negative_keywords)

mismatch_pos = df[
    (df['rating'] == 5) &
    (df['review_content'].str.contains(pattern, na=False))
]
print(f'5점인데 부정 키워드 포함: {len(mismatch_pos):,}건')
print('샘플:')
for _, row in mismatch_pos.head(3).iterrows():
    print(f'  [rating={row["rating"]}] {row["review_content"][:80]}')
print()

# 1점인데 긍정 키워드 포함
positive_keywords = ['좋아요', '최고', '강추', '완벽', '만족', '재구매']
pattern2 = '|'.join(positive_keywords)

mismatch_neg = df[
    (df['rating'] == 1) &
    (df['review_content'].str.contains(pattern2, na=False))
]
print(f'1점인데 긍정 키워드 포함: {len(mismatch_neg):,}건')
print('샘플:')
for _, row in mismatch_neg.head(3).iterrows():
    print(f'  [rating={row["rating"]}] {row["review_content"][:80]}')

# ================================================================
# [4번] 노이즈 - 광고/협찬 리뷰
# ================================================================
print('\n=== [4번] 광고/협찬 리뷰 체크 ===\n')

ad_keywords = ['협찬', '체험단', '제공받', '무상으로', '무료로 받', '서포터즈', '리뷰어']
for kw in ad_keywords:
    count = df['review_content'].str.contains(kw, na=False).sum()
    print(f'  "{kw}" 포함: {count:,}건')

ad_pattern = '|'.join(ad_keywords)
ad_reviews = df[df['review_content'].str.contains(ad_pattern, na=False)]
print(f'\n  광고/협찬 의심 총합 (중복제거): {len(ad_reviews):,}건 ({len(ad_reviews)/len(df)*100:.1f}%)')
print('\n  샘플:')
for _, row in ad_reviews.head(3).iterrows():
    print(f'  [rating={row["rating"]}, keyword={row["keyword"]}] {row["review_content"][:80]}')

# ================================================================
# [4번] 노이즈 - 도배 리뷰 (내용 중복)
# ================================================================
print('\n=== [4번] 도배 리뷰 (본문 중복) 체크 ===\n')

# 앞 50자 기준으로 중복 확인
df['content_prefix'] = df['review_content'].str[:50]
dup_content = df[df.duplicated(subset=['content_prefix'], keep=False)]
dup_groups = df['content_prefix'].value_counts()
dup_groups = dup_groups[dup_groups > 1]

print(f'  동일 내용(앞 50자 기준) 중복 그룹 수: {len(dup_groups)}개')
print(f'  중복에 해당하는 리뷰 수: {len(dup_content):,}건')
print('\n  가장 많이 반복된 내용 TOP 5:')
for text, count in dup_groups.head(5).items():
    print(f'  ({count}회) "{text[:60]}"')
