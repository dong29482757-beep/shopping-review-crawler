"""
한국어 전처리: 형태소 분석(Okt) + 품사 필터링 + 불용어 제거.

이전 버전은 정규식으로 음절만 잘라내거나(`re.findall(r"[가-힣]{2,}")`) 조사를
그대로 토큰에 포함시켜서 TF-IDF 품질이 떨어졌었다 (예: "좋아요"/"좋아서"/"좋은데"가
전부 다른 토큰으로 취급됨). Okt로 형태소 분석 후 어간(stem)으로 정규화하고,
의미 없는 조사/어미/접사는 품사 태그로 걸러내고, 주제와 무관한 범용 명사·동사는
불용어 리스트로 추가 제거한다.
"""
import re
import functools
from konlpy.tag import Okt

_okt = Okt()

# Okt가 사전에 없는 화장품 도메인 복합명사를 잘못 쪼개는 문제 대응
# (예: "재구매"->"재"+"구매", "비추천"->"비"+"추천", "발림성"->"발림"+"성은")
# 분석 전에 플레이스홀더로 치환해서 분리를 막고, 분석 후 원래 단어로 되돌린다.
_DOMAIN_TERMS = [
    "재구매", "비추천", "발림성", "보습력", "흡수력", "지속력", "가성비",
    "자극성", "끈적임", "산뜻함", "트러블", "민감성", "각질", "피지",
]
_ALPHA = "abcdefghijklmnopqrstuvwxyz"
_PLACEHOLDER = {term: f"qzterm{_ALPHA[i]}" for i, term in enumerate(_DOMAIN_TERMS)}
_PLACEHOLDER_REV = {v: k for k, v in _PLACEHOLDER.items()}

# 형태소 분석에서 남길 품사: 명사, 동사, 형용사, 부사 (감성/주제 정보를 담음)
KEEP_POS = {"Noun", "Verb", "Adjective", "Adverb"}

# 품사 필터링 후에도 남는, 리뷰 분석에 의미 없는 범용 단어
STOPWORDS = {
    "제품", "사용", "구매", "사용중", "사용하다", "사용해", "있다", "없다", "되다",
    "하다", "이다", "같다", "거", "것", "수", "때", "정도", "조금", "그냥", "진짜",
    "정말", "완전", "그리고", "근데", "그런데", "이거", "저거", "이번", "원래",
    "이제", "보다", "주다", "받다", "가다", "오다", "보이다", "있는", "없는",
    "구입", "배송", "주문", "리뷰", "후기", "사고", "쓰다", "쓰는",
}


@functools.lru_cache(maxsize=200000)
def tokenize(text):
    """리뷰 텍스트 -> 정제된 형태소 토큰 리스트. lru_cache로 중복 리뷰 재계산 방지."""
    if not isinstance(text, str) or not text.strip():
        return tuple()
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"[^\w\s가-힣]", " ", text)
    for term, placeholder in _PLACEHOLDER.items():
        text = text.replace(term, placeholder)
    try:
        pos_tags = _okt.pos(text, norm=True, stem=True)
    except Exception:
        return tuple()
    tokens = []
    for word, pos in pos_tags:
        if word in _PLACEHOLDER_REV:
            tokens.append(_PLACEHOLDER_REV[word])
            continue
        if pos in KEEP_POS and len(word) > 1 and word not in STOPWORDS:
            tokens.append(word)
    return tuple(tokens)


def clean_for_vectorizer(text):
    """TF-IDF에 넣을 공백 구분 토큰 문자열."""
    return " ".join(tokenize(text))
