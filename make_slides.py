# -*- coding: utf-8 -*-
"""5분 발표용 슬라이드 생성 (python-pptx)."""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION

NAVY = RGBColor(0x1E, 0x27, 0x61)
ICE = RGBColor(0xCA, 0xDC, 0xFC)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
CORAL = RGBColor(0xF9, 0x61, 0x67)
DARK = RGBColor(0x21, 0x29, 0x5C)
GREY = RGBColor(0x55, 0x5A, 0x6E)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


def add_slide(bg=WHITE):
    s = prs.slides.add_slide(BLANK)
    rect = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    rect.fill.solid()
    rect.fill.fore_color.rgb = bg
    rect.line.fill.background()
    rect.shadow.inherit = False
    s.shapes._spTree.remove(rect._element)
    s.shapes._spTree.insert(2, rect._element)
    return s


def add_text(slide, text, x, y, w, h, size=18, color=DARK, bold=False, align=PP_ALIGN.LEFT,
             font="Calibri", anchor=MSO_ANCHOR.TOP, italic=False, line_spacing=None):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    lines = text.split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if line_spacing:
            p.line_spacing = line_spacing
        r = p.add_run()
        r.text = line
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.color.rgb = color
        r.font.name = font
    return box


def add_bullets(slide, items, x, y, w, h, size=15, color=DARK, font="Calibri", space_after=8):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(space_after)
        r = p.add_run()
        r.text = "•  " + item
        r.font.size = Pt(size)
        r.font.color.rgb = color
        r.font.name = font
    return box


def add_chip(slide, text, x, y, w, h, fill, text_color=WHITE, size=12, bold=True):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.adjustments[0] = 0.5
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    shp.line.fill.background()
    shp.shadow.inherit = False
    tf = shp.text_frame
    tf.word_wrap = False
    tf.margin_left = Inches(0.05); tf.margin_right = Inches(0.05)
    tf.margin_top = 0; tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = text_color
    return shp


def add_stat(slide, number, label, x, y, w, h, number_color=NAVY, label_color=GREY):
    add_text(slide, number, x, y, w, h * 0.62, size=40, color=number_color, bold=True,
              align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.BOTTOM)
    add_text(slide, label, x, y + h * 0.62, w, h * 0.38, size=13, color=label_color,
              align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.TOP)


# ---------- Slide 1: Title ----------
s = add_slide(NAVY)
add_text(s, "BeautyScope", 1, 2.5, 11.3, 1.2, size=54, color=WHITE, bold=True, font="Georgia")
add_text(s, "화장품 리뷰 538,774건으로 만든 감성 분석 서비스", 1, 3.75, 11.3, 0.6,
         size=20, color=ICE, font="Calibri")
add_text(s, "쿠팡 · 무신사 · 올리브영 데이터 통합 → ML/DL 감성 분류 모델 → Streamlit 서비스",
         1, 4.4, 11.3, 0.5, size=14, color=ICE, italic=True)
add_chip(s, "데이터 수집", 1, 5.6, 1.8, 0.45, CORAL)
add_chip(s, "모델 학습 (ML+DL)", 2.95, 5.6, 2.3, 0.45, CORAL)
add_chip(s, "Streamlit 배포", 5.4, 5.6, 2.0, 0.45, CORAL)

# ---------- Slide 2: 문제 정의 ----------
s = add_slide(WHITE)
add_text(s, "문제 정의", 0.7, 0.5, 6, 0.8, size=32, color=NAVY, bold=True, font="Georgia")
add_bullets(s, [
    "화장품 리뷰는 플랫폼마다 수만~수십만 건 — 사람이 다 읽고 판단하기 어렵다",
    "별점만으로는 \"왜\" 좋고 나쁜지 알 수 없다 (텍스트 안에 진짜 정보가 있음)",
    "여러 플랫폼(쿠팡/무신사/올리브영) 리뷰를 한 기준으로 비교하기 어렵다",
], 0.7, 1.7, 6.0, 3.5, size=17)
add_text(s, "그래서: 리뷰 텍스트를 긍정/중립/부정으로 자동 분류하고,\n플랫폼 통합 대시보드로 한눈에 보여주는 서비스를 만든다",
         0.7, 5.3, 6.0, 1.5, size=16, color=CORAL, bold=True, line_spacing=1.3)

box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.1), Inches(1.6), Inches(5.6), Inches(5.3))
box.adjustments[0] = 0.04
box.fill.solid(); box.fill.fore_color.rgb = RGBColor(0xF4, 0xF6, 0xFC)
box.line.fill.background(); box.shadow.inherit = False
add_text(s, "별점만 본다면?", 7.5, 1.95, 4.8, 0.5, size=16, bold=True, color=NAVY)
add_text(s,
         "★★★★★\n\"보습력은 좋은데 향이 너무 강해서\n다시는 안 살 것 같아요\"\n\n"
         "→ 별점은 5점, 하지만 텍스트는 단점(향)을 말하고 있다.\n"
         "감성 분류 모델은 이런 \"숨은 신호\"를 텍스트에서 직접 잡아낸다.",
         7.5, 2.6, 4.8, 4.0, size=14.5, color=GREY, line_spacing=1.35)

# ---------- Slide 3: 데이터 수집 현황 ----------
s = add_slide(WHITE)
add_text(s, "데이터 수집 현황", 0.7, 0.5, 8, 0.8, size=32, color=NAVY, bold=True, font="Georgia")
add_text(s, "3개 플랫폼 통합 538,774건", 0.7, 1.25, 8, 0.5, size=15, color=GREY)

stats = [("86,379", "쿠팡"), ("230,870", "무신사"), ("221,525", "올리브영"), ("538,774", "통합 전체")]
colors = [CORAL, NAVY, NAVY, NAVY]
sx = 0.7
sw = 2.85
for i, (num, label) in enumerate(stats):
    add_stat(s, num, label, sx + i * (sw + 0.15), 2.1, sw, 1.7,
              number_color=colors[i])

chart_data = CategoryChartData()
chart_data.categories = ["쿠팡", "무신사", "올리브영"]
chart_data.add_series("건수", (86379, 230870, 221525))
gframe = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.7), Inches(4.2), Inches(5.6), Inches(2.9), chart_data)
chart = gframe.chart
chart.has_legend = False
plot = chart.plots[0]
plot.series[0].format.fill.solid()
plot.series[0].format.fill.fore_color.rgb = NAVY

add_text(s, "데이터 장점", 6.8, 4.2, 5.9, 0.4, size=16, bold=True, color=NAVY)
add_bullets(s, [
    "별점 기반 라벨이 이미 존재 → 별도 수작업 레이블링 불필요",
    "화장품 도메인 특화 (성분/지속력/자극 등 표현이 풍부)",
    "2015~2026년 10년치 데이터로 트렌드 분석 가능",
    "20개+ 카테고리로 비교 분석 용이",
], 6.8, 4.7, 5.9, 2.4, size=13.5)

# ---------- Slide 4: 데이터 준비의 어려움 ----------
s = add_slide(WHITE)
add_text(s, "데이터 준비 — 가장 어려웠던 단계", 0.7, 0.5, 11.5, 0.8, size=30, color=NAVY, bold=True, font="Georgia")

issues = [
    ("스키마 불일치", "쿠팡/무신사/올리브영 컬럼명이 전부 다름\n(CSV 2종 + JSONL 4파일)",
     "공통 스키마로 변환하는 로더 3개 작성 후 concat"),
    ("라벨 기준 불일치 (핵심)", "무신사 sentiment는 별점 기반이 아니라 텍스트 분석 기반\n→ 5점 리뷰의 21%가 '부정'으로 라벨링되어 있었음",
     "전체 데이터의 sentiment를 별점에서 일괄 재계산해 기준 통일"),
    ("인코딩 깨짐", "무신사 CSV를 기본 인코딩으로 읽으면\n한글이 깨짐 (mojibake)",
     "encoding='utf-8-sig' 명시"),
    ("클래스 불균형", "긍정 86.7% vs 부정 8.2% vs 중립 5.1%\n→ 그냥 다 긍정 찍어도 86% 정확도",
     "부정/중립 전량 + 긍정은 2배 규모로만 다운샘플링"),
]
y = 1.55
for title, problem, solution in issues:
    card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(y), Inches(11.9), Inches(1.28))
    card.adjustments[0] = 0.06
    card.fill.solid(); card.fill.fore_color.rgb = RGBColor(0xF4, 0xF6, 0xFC)
    card.line.fill.background(); card.shadow.inherit = False
    add_chip(s, title, 0.95, y + 0.18, 2.55, 0.45, CORAL, size=12.5)
    add_text(s, problem, 3.75, y + 0.1, 4.1, 1.05, size=12, color=GREY, line_spacing=1.15)
    add_text(s, "해결 → " + solution, 8.0, y + 0.1, 4.45, 1.05, size=12, color=NAVY, bold=True, line_spacing=1.15)
    y += 1.4

# ---------- Slide 5: AI 활용 / 환경 제약 ----------
s = add_slide(NAVY)
add_text(s, "구현하며 AI를 어떻게 활용했나", 0.7, 0.5, 11.5, 0.8, size=30, color=WHITE, bold=True, font="Georgia")
add_bullets(s, [
    "Claude Code로 전처리 스크립트·모델 코드·Streamlit 앱을 페어 프로그래밍 방식으로 작성",
    "데이터 검증(rating vs sentiment 크로스탭)을 코드로 직접 돌려 라벨 불일치를 수치로 확인",
    "환경 제약(PyTorch 미설치)을 만났을 때 대체 구현 방향을 같이 설계",
], 0.7, 1.6, 6.1, 3.0, size=15.5, color=WHITE)

box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.1), Inches(1.5), Inches(5.6), Inches(5.3))
box.adjustments[0] = 0.04
box.fill.solid(); box.fill.fore_color.rgb = RGBColor(0x28, 0x33, 0x70)
box.line.fill.background(); box.shadow.inherit = False
add_text(s, "예상치 못한 벽: PyTorch 설치 실패", 7.5, 1.8, 4.8, 0.6, size=16, bold=True, color=CORAL)
add_text(s,
         "환경의 Python이 3.14라서 PyTorch/TensorFlow\n휠이 아직 배포되지 않음\n"
         "→ pip install torch: No matching distribution\n\n"
         "해결: 신경망 프레임워크 없이 numpy로\n순전파·역전파를 직접 구현\n\n"
         "결과적으로 \"신경망이 어떻게 학습되는지\"를\n더 명확하게 설명할 수 있는 발표 소재가 됨",
         7.5, 2.5, 4.8, 4.0, size=14, color=WHITE, line_spacing=1.4)

# ---------- Slide 6: 신경망 구성 ----------
s = add_slide(WHITE)
add_text(s, "DL 모델 — numpy로 직접 구현한 신경망", 0.7, 0.5, 11.5, 0.8, size=28, color=NAVY, bold=True, font="Georgia")

layers = [("입력\nTF-IDF\n20,000차원", RGBColor(0xCA,0xDC,0xFC)),
          ("Dense 128\nReLU", NAVY),
          ("Dense 64\nReLU", NAVY),
          ("Dense 3\nSoftmax", CORAL)]
lx = 0.9
lw = 2.55
ly = 1.7
lh = 1.7
for i, (label, color) in enumerate(layers):
    shp = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(lx + i*(lw+0.4)), Inches(ly), Inches(lw), Inches(lh))
    shp.adjustments[0] = 0.08
    shp.fill.solid(); shp.fill.fore_color.rgb = color
    shp.line.fill.background(); shp.shadow.inherit = False
    tcolor = NAVY if color == RGBColor(0xCA,0xDC,0xFC) else WHITE
    tf = shp.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    for j, line in enumerate(label.split("\n")):
        pp = p if j == 0 else tf.add_paragraph()
        pp.alignment = PP_ALIGN.CENTER
        r = pp.add_run(); r.text = line
        r.font.size = Pt(14); r.font.bold = True; r.font.color.rgb = tcolor
    if i < len(layers) - 1:
        arrow_x = lx + i*(lw+0.4) + lw + 0.02
        arr = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(arrow_x), Inches(ly + lh/2 - 0.12), Inches(0.36), Inches(0.24))
        arr.fill.solid(); arr.fill.fore_color.rgb = GREY
        arr.line.fill.background(); arr.shadow.inherit = False

add_text(s, "학습 방식", 0.9, 3.8, 5.6, 0.4, size=15, bold=True, color=NAVY)
add_bullets(s, [
    "Mini-batch SGD + Momentum(0.9), L2 정규화",
    "learning rate 0.08 → epoch마다 0.92배 감소",
    "batch size 256, 15 epoch, 학습시간 약 132초",
    "scipy sparse(TF-IDF) × dense 가중치 행렬곱을\nbackprop 수식에 맞춰 직접 구현",
], 0.9, 4.25, 5.6, 2.8, size=13.5)

add_text(s, "데이터 규모", 6.9, 3.8, 5.6, 0.4, size=15, bold=True, color=NAVY)
add_bullets(s, [
    "학습 데이터: 136,150건 (밸런싱 후)",
    "검증 데이터: 24,026건",
    "원본 통합 데이터: 538,774건",
], 6.9, 4.25, 5.6, 1.6, size=13.5)
box2 = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(5.6), Inches(5.6), Inches(1.4))
box2.adjustments[0]=0.08
box2.fill.solid(); box2.fill.fore_color.rgb = RGBColor(0xF4,0xF6,0xFC)
box2.line.fill.background(); box2.shadow.inherit = False
add_text(s, "관찰: epoch 4 근처(acc 0.781) 이후\ntrain loss는 계속 감소하지만 test acc는\n진동/하락 → 과적합 신호를 직접 확인",
         7.1, 5.7, 5.2, 1.2, size=12.5, color=GREY, line_spacing=1.25)

# ---------- Slide 7: ML vs DL 결과 ----------
s = add_slide(WHITE)
add_text(s, "ML vs DL 결과 비교", 0.7, 0.5, 8, 0.8, size=30, color=NAVY, bold=True, font="Georgia")

chart_data2 = CategoryChartData()
chart_data2.categories = ["Accuracy", "Macro F1"]
chart_data2.add_series("ML (TF-IDF+LogReg)", (0.738, 0.677))
chart_data2.add_series("DL (numpy 신경망)", (0.762, 0.663))
gframe2 = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.7), Inches(1.6), Inches(6.4), Inches(4.0), chart_data2)
chart2 = gframe2.chart
chart2.has_legend = True
chart2.legend.position = XL_LEGEND_POSITION.BOTTOM
chart2.legend.include_in_layout = False
chart2.plots[0].series[0].format.fill.solid()
chart2.plots[0].series[0].format.fill.fore_color.rgb = NAVY
chart2.plots[0].series[1].format.fill.solid()
chart2.plots[0].series[1].format.fill.fore_color.rgb = CORAL

add_text(s, "공통적으로 어려운 클래스: 중립", 7.5, 1.7, 5.3, 0.4, size=16, bold=True, color=NAVY)
add_bullets(s, [
    "ML neutral F1: 0.45  /  DL neutral F1: 0.37",
    "중립(별점 3점)은 텍스트 신호 자체가 모호한\n근본적으로 어려운 라벨",
    "가벼운 ML이 매크로 F1 기준 더 안정적",
    "신경망은 정확도는 약간 높지만 과적합 경향",
], 7.5, 2.25, 5.3, 3.2, size=13.5)

note = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(5.8), Inches(11.9), Inches(1.0))
note.adjustments[0]=0.1
note.fill.solid(); note.fill.fore_color.rgb = RGBColor(0xF4,0xF6,0xFC)
note.line.fill.background(); note.shadow.inherit = False
add_text(s, "결론: 단순 TF-IDF 특징에서는 모델 복잡도보다 데이터 라벨 품질이 성능을 더 좌우했다",
         1.0, 6.05, 11.3, 0.5, size=14.5, bold=True, color=CORAL, align=PP_ALIGN.CENTER)

# ---------- Slide 8: 서비스 데모 ----------
s = add_slide(WHITE)
add_text(s, "Streamlit 서비스 — BeautyScope", 0.7, 0.5, 11.5, 0.8, size=30, color=NAVY, bold=True, font="Georgia")

tabs = [
    ("🔍 감성 분석 데모", "리뷰 텍스트 입력 → ML/DL\n동시 예측 + 확률 시각화"),
    ("📊 데이터 대시보드", "플랫폼/별점/트렌드/카테고리별\n분포, 부정·긍정 다빈도 키워드"),
    ("ℹ️ 프로젝트 소개", "데이터 규모, 모델 성능,\nDEVLOG 링크"),
]
tx = 0.7
tw = 3.85
for i, (title, desc) in enumerate(tabs):
    card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(tx + i*(tw+0.2)), Inches(1.7), Inches(tw), Inches(2.3))
    card.adjustments[0] = 0.08
    card.fill.solid(); card.fill.fore_color.rgb = NAVY if i != 1 else CORAL
    card.line.fill.background(); card.shadow.inherit = False
    add_text(s, title, tx + i*(tw+0.2) + 0.25, 1.95, tw - 0.5, 0.5, size=16, bold=True, color=WHITE)
    add_text(s, desc, tx + i*(tw+0.2) + 0.25, 2.55, tw - 0.5, 1.2, size=13, color=ICE, line_spacing=1.3)

add_text(s, "동작 확인", 0.7, 4.3, 11.5, 0.4, size=16, bold=True, color=NAVY)
add_bullets(s, [
    "로컬 환경에서 streamlit run app.py 실행 → HTTP 200 응답 확인",
    "예시 리뷰 \"향이 너무 강하고 트러블 났어요\" 입력 → ML/DL 모두 negative(부정) 예측 일치",
    "예시 리뷰 \"촉촉하고 흡수도 잘 되고 좋아요\" 입력 → ML/DL 모두 positive(긍정) 예측 일치",
], 0.7, 4.8, 11.5, 1.8, size=14)

# ---------- Slide 9: 배포 준비 ----------
s = add_slide(WHITE)
add_text(s, "배포 준비", 0.7, 0.5, 8, 0.8, size=32, color=NAVY, bold=True, font="Georgia")
add_bullets(s, [
    "requirements.txt로 의존성 고정 (scikit-learn, streamlit, pandas, numpy, scipy, joblib)",
    "학습된 모델(tfidf_vectorizer.joblib, ml_logreg.joblib, dl_ffnn.npz) 리포에 포함\n→ 재학습 없이 바로 서비스 구동 가능",
    "538,774건 원본 대신 사전 집계 CSV(agg_*.csv)를 대시보드가 읽도록 분리 → 로딩 속도 개선",
    "대용량 원본 크롤링 CSV는 .gitignore 처리, 정제된 merged_reviews_all.csv만 추적",
], 0.7, 1.7, 11.5, 3.5, size=16)

box3 = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(5.5), Inches(11.9), Inches(1.3))
box3.adjustments[0]=0.08
box3.fill.solid(); box3.fill.fore_color.rgb = RGBColor(0xF4,0xF6,0xFC)
box3.line.fill.background(); box3.shadow.inherit = False
add_text(s, "다음 과제: 대용량 데이터 Git LFS/외부 스토리지 연동, early stopping으로\nDL 과적합 개선, klue/bert 등 사전학습 모델 파인튜닝(GPU/호환 Python 환경 확보 시)",
         1.0, 5.75, 11.3, 0.9, size=14, color=GREY, line_spacing=1.3)

# ---------- Slide 10: 마무리 ----------
s = add_slide(NAVY)
add_text(s, "정리", 1, 1.3, 11.3, 0.8, size=36, color=WHITE, bold=True, font="Georgia")
add_bullets(s, [
    "3개 플랫폼 538,774건 데이터를 통일된 기준으로 통합 (가장 큰 난관: 라벨 기준 불일치)",
    "환경 제약(PyTorch 미설치)에 막혔지만 numpy로 신경망을 직접 구현해 ML/DL을 비교",
    "ML accuracy 0.738 / DL accuracy 0.762 — 모델보다 데이터 라벨 품질이 핵심이었다는 결론",
    "Streamlit으로 감성 분석 데모 + 데이터 대시보드를 구현하고 동작까지 검증",
], 1, 2.4, 11.0, 3.5, size=18, color=WHITE)
add_text(s, "BeautyScope", 1, 6.3, 11.3, 0.6, size=20, color=CORAL, bold=True, font="Georgia")

prs.save(r"D:\crolling\BeautyScope_발표.pptx")
print("저장 완료")
