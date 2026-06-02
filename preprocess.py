import pandas as pd
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 완료본 파일만 사용 (partial은 이미 최종본에 포함됨)
SOURCE_FILES = [
    'coupang_reviews_20260514_001626.csv',
    'coupang_reviews_20260514_224303.csv',
]

print('=== 1. 파일 로드 및 병합 ===')
dfs = []
for f in SOURCE_FILES:
    df = pd.read_csv(f, encoding='utf-8-sig')
    print(f'  {f}: {len(df):,}건')
    dfs.append(df)

combined = pd.concat(dfs, ignore_index=True)
print(f'\n병합 후: {len(combined):,}건')

# 중복 제거 (review_id 기준)
before = len(combined)
combined = combined.drop_duplicates(subset=['review_id'])
print(f'중복 제거 후: {len(combined):,}건 (제거: {before - len(combined):,}건)')

print('\n=== 2. 텍스트 정제 ===')

def clean_text(text):
    if pd.isna(text):
        return ''
    text = str(text)
    # zero-width space 등 불필요한 유니코드 제거
    text = re.sub(r'[​‌‍﻿]', '', text)
    # 과도한 줄바꿈/공백 정규화
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    # 앞뒤 공백 제거
    text = text.strip()
    return text

def clean_product_name(text):
    if pd.isna(text) or text == '':
        return ''
    text = str(text)
    # 가격/할인율/배송 정보 제거 (숫자+원, %, 배송 문구 등)
    text = re.sub(r'\d[\d,]*원.*', '', text)
    text = re.sub(r'\d+%.*', '', text)
    text = re.sub(r'(로켓|내일|오늘|무료|배송).*', '', text)
    text = text.strip().rstrip(',').strip()
    return text

combined['review_content'] = combined['review_content'].apply(clean_text)
combined['review_title'] = combined['review_title'].apply(clean_text)
combined['product_name'] = combined['product_name'].apply(clean_product_name)

print('  텍스트 정제 완료')

print('\n=== 3. 짧은 리뷰 필터링 (본문 10자 미만) ===')
before = len(combined)
combined = combined[combined['review_content'].str.len() >= 10]
print(f'  필터링 후: {len(combined):,}건 (제거: {before - len(combined):,}건)')

print('\n=== 4. 감성 레이블 추가 ===')
def get_sentiment(rating):
    if rating >= 4:
        return 'positive'
    elif rating <= 2:
        return 'negative'
    else:
        return 'neutral'

combined['sentiment'] = combined['rating'].apply(get_sentiment)
print('  sentiment 분포:')
print(combined['sentiment'].value_counts().to_string())

print('\n=== 5. 날짜 형식 정규화 ===')
# 엑셀 시리얼 넘버 → 날짜 변환 (origin: 1899-12-30)
def parse_date(val):
    if pd.isna(val):
        return None
    try:
        val = float(val)
        return pd.Timestamp('1899-12-30') + pd.Timedelta(days=val)
    except:
        return pd.to_datetime(val, errors='coerce')

combined['review_date'] = combined['review_date'].apply(parse_date)
combined['review_date'] = pd.to_datetime(combined['review_date'], errors='coerce').dt.strftime('%Y-%m-%d')
print(f'  날짜 변환 실패(NaT): {combined["review_date"].isna().sum()}건')
print(f'  날짜 범위: {combined["review_date"].min()} ~ {combined["review_date"].max()}')

print('\n=== 6. 컬럼 정리 ===')
combined = combined[[
    'review_id', 'product_id', 'product_name',
    'keyword', 'rating', 'sentiment',
    'review_title', 'review_content',
    'review_date', 'nickname'
]]

# 최종 결측값 처리 (빈 문자열로 통일 → CSV 재로딩 시 NaN 방지)
combined['product_name'] = combined['product_name'].fillna('')
combined['nickname'] = combined['nickname'].fillna('')
combined['review_title'] = combined['review_title'].fillna('')

print(f'\n최종 결측값:')
print(combined.isnull().sum().to_string())

print('\n=== 최종 저장 ===')
output_file = 'coupang_reviews_final.csv'
combined.to_csv(output_file, index=False, encoding='utf-8-sig', na_rep='')
print(f'저장 완료: {output_file} ({len(combined):,}건)')

print('\n=== 최종 현황 ===')
print(f'총 건수: {len(combined):,}')
print(f'키워드 수: {combined["keyword"].nunique()}개')
print(f'상품 수: {combined["product_id"].nunique():,}개')
print(f'기간: {combined["review_date"].min()} ~ {combined["review_date"].max()}')
