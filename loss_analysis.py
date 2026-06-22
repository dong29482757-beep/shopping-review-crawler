import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

original = 112971

steps = [
    ("원본 병합", 112971, ""),
    ("중복 제거 (review_id)", 108022, "같은 리뷰가 두 번 크롤링됨"),
    ("10자 미만 제거", 107193, "본문 없는 리뷰"),
    ("체험단/협찬 제거", 87409, "협찬·체험단·제공받 키워드"),
    ("도배 제거 (앞50자 중복)", 86379, "동일 문구 반복"),
]

print('=== 단계별 제거 현황 ===\n')
print(f'{"단계":<25} {"건수":>8} {"제거":>8} {"비율":>7}  {"사유"}')
print('-' * 75)
prev = original
for name, count, reason in steps:
    removed = prev - count
    pct = removed / original * 100 if removed > 0 else 0
    print(f'{name:<25} {count:>8,} {removed:>8,} {pct:>6.1f}%  {reason}')
    prev = count

print(f'\n총 제거: {original - 86379:,}건 ({(original-86379)/original*100:.1f}%)')
print(f'최종 잔존: 86,379건 ({86379/original*100:.1f}%)')

# 핵심: 체험단 제거가 맞는 선택이었나?
print('\n=== 체험단 리뷰 특성 분석 ===')
df_all = pd.concat([
    pd.read_csv('coupang_reviews_20260514_001626.csv', encoding='utf-8-sig'),
    pd.read_csv('coupang_reviews_20260514_224303.csv', encoding='utf-8-sig'),
], ignore_index=True).drop_duplicates(subset=['review_id'])

ad_pattern = '협찬|체험단|제공받|무상으로|무료로 받|리뷰어'
ad = df_all[df_all['review_content'].astype(str).str.contains(ad_pattern, na=False)]
non_ad = df_all[~df_all['review_content'].astype(str).str.contains(ad_pattern, na=False)]

print(f'체험단 리뷰 평균 별점: {pd.to_numeric(ad["rating"], errors="coerce").mean():.2f}점')
print(f'일반 리뷰 평균 별점:   {pd.to_numeric(non_ad["rating"], errors="coerce").mean():.2f}점')

ad_5 = (pd.to_numeric(ad["rating"], errors="coerce") == 5).sum()
print(f'체험단 중 5점 비율: {ad_5/len(ad)*100:.1f}%')
non_5 = (pd.to_numeric(non_ad["rating"], errors="coerce") == 5).sum()
print(f'일반 중 5점 비율:   {non_5/len(non_ad)*100:.1f}%')
