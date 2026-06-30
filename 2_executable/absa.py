"""
속성기반 감성분석 (Aspect-Based Sentiment Analysis), 규칙 기반.

기존 서비스는 "리뷰 텍스트를 넣으면 감성 하나를 반환"하는 데모였는데, 실제로
화장품을 살지 말지 고민하는 사람에게는 "이 제품이 보습력은 좋은데 향이
별로다" 같은 속성별 정보가 더 유용하다. ML 분류기를 538,774건 전체에
돌리려면 Okt 형태소분석이 병목(200건/s 수준)이라 비용이 너무 크므로,
정규식 기반 키워드 매칭 + 부정어 처리로 빠르게 속성별 긍부정을 추출한다.
정확도는 ML 분류기보다 거칠지만 538,774건 전체를 수 초 내에 처리 가능하다.
"""
import re

ASPECTS = {
    "보습/수분": ["보습", "수분", "촉촉", "건조함", "당김", "속건조"],
    "향": ["향이", "향도", "냄새", "스멜", "체취"],
    "트러블/자극": ["트러블", "자극", "뒤집", "여드름", "따가움", "따갑", "가렵", "붉어짐", "뾰루지"],
    "발림성/흡수력": ["발림", "흡수", "끈적", "산뜻", "가볍게", "무겁게", "결대로"],
    "지속력": ["지속력", "오래가", "금방 지워", "쉽게 지워", "유지력"],
    "가격/가성비": ["가성비", "가격이", "비싸", "저렴", "가격대비"],
    "용기/디자인": ["용기가", "펌프", "디자인", "튜브", "패키지"],
    "효과": ["효과", "좋아졌", "개선", "변화가", "효과가"],
}

NEGATION = ["안 ", "않", "별로", "전혀", "아니", "못 "]

POS_WORDS = [
    "좋", "만족", "최고", "추천", "재구매", "촉촉", "산뜻", "부드럽", "순하",
    "맘에", "마음에", "괜찮", "훌륭", "강추", "성공", "대박",
]
NEG_WORDS = [
    "별로", "안좋", "안 좋", "최악", "비추", "트러블", "자극", "건조",
    "끈적", "답답", "심하", "안남", "별루", "실망", "환불", "후회", "비싸",
]

CLAUSE_SPLIT = re.compile(
    r"[.!?~\n,]|그런데|근데|하지만|그래도|단지|다만|그치만"
    r"|았는데|었는데|는데|은데|한데|인데|운데|지만"
)


def split_clauses(text):
    if not isinstance(text, str):
        return []
    return [c.strip() for c in CLAUSE_SPLIT.split(text) if c.strip()]


def score_sentiment(clause):
    """clause 안의 긍/부정 키워드 점수. 부정어가 긍정어 앞 8자 내에 있으면 반전."""
    pos = 0
    neg = 0
    for w in POS_WORDS:
        for m in re.finditer(re.escape(w), clause):
            window = clause[max(0, m.start() - 8):m.start()]
            if any(neg_word in window for neg_word in NEGATION):
                neg += 1
            else:
                pos += 1
    for w in NEG_WORDS:
        neg += len(re.findall(re.escape(w), clause))
    if pos == 0 and neg == 0:
        return None
    return "positive" if pos > neg else "negative"


def extract_aspect_sentiments(review_text, fallback_sentiment=None):
    """리뷰 본문 -> [(aspect, sentiment), ...] 리스트."""
    results = []
    clauses = split_clauses(review_text)
    if not clauses:
        return results
    for clause in clauses:
        matched_aspects = [
            aspect for aspect, keywords in ASPECTS.items()
            if any(kw in clause for kw in keywords)
        ]
        if not matched_aspects:
            continue
        sentiment = score_sentiment(clause)
        if sentiment is None:
            sentiment = fallback_sentiment
        if sentiment is None:
            continue
        for aspect in matched_aspects:
            results.append((aspect, sentiment))
    return results
