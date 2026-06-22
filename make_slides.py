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
add_text(s, "BeautyScope", 1, 2.2, 11.3, 1.2, size=54, color=WHITE, bold=True, font="Georgia")
add_text(s, "화장품 리뷰 538,774건으로 만든 감성 분석 + 속성기반 리포트 서비스", 1, 3.45, 11.3, 0.6,
         size=19, color=ICE, font="Calibri")
add_text(s, "쿠팡 → 무신사·올리브영 추가 수집 → ML/DL 감성분류 → 속성분석(ABSA) → Streamlit 배포",
         1, 4.1, 11.3, 0.5, size=13.5, color=ICE, italic=True)
add_chip(s, "데이터 수집", 1, 5.4, 1.8, 0.45, CORAL)
add_chip(s, "모델 학습 (ML+DL)", 2.95, 5.4, 2.3, 0.45, CORAL)
add_chip(s, "속성분석(ABSA)", 5.4, 5.4, 2.0, 0.45, CORAL)
add_chip(s, "Streamlit 배포", 7.55, 5.4, 2.0, 0.45, CORAL)

# ---------- Slide 2: 문제정의 + 데이터 수집 ----------
s = add_slide(WHITE)
add_text(s, "문제정의 & 데이터 수집", 0.7, 0.5, 11.5, 0.8, size=30, color=NAVY, bold=True, font="Georgia")
add_bullets(s, [
    "리뷰가 상품당 수백~수천 건 — 사람이 다 읽고 판단하기 어렵다",
    "별점만 봐서는 \"왜\" 좋고 나쁜지, 속성별로(보습/향/트러블) 어떤지 알 수 없다",
    "→ ML/DL로 감성 분류 + 속성기반 감성분석(ABSA)으로 해결",
], 0.7, 1.5, 11.5, 1.8, size=15.5)

stages = [
    ("1차", "쿠팡 크롤링\n(20개 키워드)", "86,379건"),
    ("2차", "+ 무신사·올리브영\n(동료 크롤링 데이터 추가)", "452,395건"),
    ("최종", "스키마/라벨 통일\n+ 중복 제거", "538,774건"),
]
sx = 0.7
sw = 3.85
for i, (stage, label, count) in enumerate(stages):
    color = CORAL if i == len(stages) - 1 else NAVY
    card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(sx + i*(sw+0.2)), Inches(3.6), Inches(sw), Inches(2.7))
    card.adjustments[0] = 0.08
    card.fill.solid(); card.fill.fore_color.rgb = color
    card.line.fill.background(); card.shadow.inherit = False
    add_text(s, stage, sx + i*(sw+0.2) + 0.25, 3.85, sw-0.5, 0.4, size=14, bold=True, color=ICE)
    add_text(s, label, sx + i*(sw+0.2) + 0.25, 4.3, sw-0.5, 1.0, size=15, bold=True, color=WHITE, line_spacing=1.25)
    add_text(s, count, sx + i*(sw+0.2) + 0.25, 5.5, sw-0.5, 0.6, size=24, bold=True, color=WHITE)
    if i < len(stages) - 1:
        arrow_x = sx + i*(sw+0.2) + sw + 0.02
        arr = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(arrow_x), Inches(4.8), Inches(0.16), Inches(0.35))
        arr.fill.solid(); arr.fill.fore_color.rgb = GREY
        arr.line.fill.background(); arr.shadow.inherit = False

# ---------- Slide 3: 데이터 준비 — 가장 까다로웠던 단계 ----------
s = add_slide(WHITE)
add_text(s, "데이터 준비 — 가장 까다로웠던 단계", 0.7, 0.5, 11.5, 0.8, size=28, color=NAVY, bold=True, font="Georgia")

issues = [
    ("라벨 기준 불일치 (핵심)", "무신사 sentiment가 별점 아닌 텍스트분석 기반 → 5점 리뷰의 21%가 '부정'",
     "전체 데이터의 sentiment를 별점에서 일괄 재계산"),
    ("클래스 불균형", "긍정 86.7% — 그대로 학습하면 다 긍정 찍어도 86% 정확도",
     "부정/중립 전량 + 긍정은 2배 규모로만 다운샘플링"),
    ("불용어/형태소 미처리", "정규식으로만 잘라서 조사가 토큰에 섞임 (\"좋아요\"≠\"좋아서\")",
     "Okt 형태소분석 + 어간정규화 + 불용어 제거"),
]
y = 1.7
for title, problem, solution in issues:
    card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(y), Inches(11.9), Inches(1.55))
    card.adjustments[0] = 0.06
    card.fill.solid(); card.fill.fore_color.rgb = RGBColor(0xF4, 0xF6, 0xFC)
    card.line.fill.background(); card.shadow.inherit = False
    add_chip(s, title, 0.95, y + 0.22, 3.0, 0.48, CORAL, size=13)
    add_text(s, problem, 4.15, y + 0.15, 3.85, 1.25, size=13, color=GREY, line_spacing=1.25)
    add_text(s, "해결 → " + solution, 8.15, y + 0.15, 4.3, 1.25, size=13, color=NAVY, bold=True, line_spacing=1.25)
    y += 1.75

# ---------- Slide 4: AI 활용 + 모델 비교 ----------
s = add_slide(WHITE)
add_text(s, "AI 활용 & 모델 — ML/DL/LSTM/Transformer 비교", 0.7, 0.5, 11.5, 0.8, size=24, color=NAVY, bold=True, font="Georgia")
add_bullets(s, [
    "Claude Code와 페어 프로그래밍 — crosstab으로 라벨 불일치를 수치로 진단",
    "환경 제약(Python 3.14, PyTorch 미설치) → numpy로 신경망 직접 구현,",
    "이후 Python 3.11 별도 venv 구성해서 실제 LSTM·Transformer까지 검증",
], 0.7, 1.5, 11.5, 1.7, size=14.5)

chart_data2 = CategoryChartData()
chart_data2.categories = ["ML\n(TF-IDF+LogReg)", "DL\n(numpy FFNN)", "LSTM\n(PyTorch)", "KoELECTRA\n(파인튜닝)"]
chart_data2.add_series("accuracy", (0.730, 0.754, 0.734, 0.772))
chart_data2.add_series("macro F1", (0.668, 0.664, 0.671, 0.660))
gframe2 = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.7), Inches(3.3), Inches(7.6), Inches(3.7), chart_data2)
chart2 = gframe2.chart
chart2.has_legend = True
chart2.legend.position = XL_LEGEND_POSITION.BOTTOM
chart2.legend.include_in_layout = False
chart2.plots[0].series[0].format.fill.solid()
chart2.plots[0].series[0].format.fill.fore_color.rgb = NAVY
chart2.plots[0].series[1].format.fill.solid()
chart2.plots[0].series[1].format.fill.fore_color.rgb = CORAL

add_text(s, "결론", 8.6, 3.4, 4.2, 0.4, size=15, bold=True, color=NAVY)
add_bullets(s, [
    "KoELECTRA가 데이터 1/7만 쓰고도\n최고 accuracy → 사전학습 효과 확인",
    "LSTM은 순서 정보 기대했으나 차이 없음\n→ 짧은 리뷰는 어휘 자체가 강한 신호",
], 8.6, 3.9, 4.2, 2.8, size=12.5)

# ---------- Slide 5: 모델 보정 + 서비스 전환(ABSA) ----------
s = add_slide(NAVY)
add_text(s, "모델 보정 & \"실용성 없다\" 피드백 반영", 0.7, 0.5, 11.5, 0.8, size=25, color=WHITE, bold=True, font="Georgia")

box3 = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(1.5), Inches(5.8), Inches(5.3))
box3.adjustments[0] = 0.05
box3.fill.solid(); box3.fill.fore_color.rgb = RGBColor(0x28, 0x33, 0x70)
box3.line.fill.background(); box3.shadow.inherit = False
add_text(s, "모델 문제 발견 → 보정", 1.0, 1.8, 5.1, 0.5, size=16, bold=True, color=CORAL)
add_text(s,
         "학습셋과 실제 운영 비율이 달라\nneutral precision이 0.20까지 하락\n(label shift)\n\n"
         "→ 추론 단계에서 확률 보정 추가\n(재학습 없이)\n\n"
         "ML accuracy: 0.806 → 0.909\nDL accuracy: 0.890 → 0.920",
         1.0, 2.4, 5.1, 4.0, size=14, color=WHITE, line_spacing=1.4)

box4 = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.5), Inches(5.8), Inches(5.3))
box4.adjustments[0] = 0.05
box4.fill.solid(); box4.fill.fore_color.rgb = CORAL
box4.line.fill.background(); box4.shadow.inherit = False
add_text(s, "서비스 전환: 텍스트 데모 → 상품 리포트", 7.1, 1.8, 5.2, 0.7, size=16, bold=True, color=WHITE)
add_text(s,
         "기존: 리뷰를 직접 타이핑해야 하는 데모\n→ 실용성 없다는 피드백\n\n"
         "전환: 상품 검색 → 속성별(8개) 장단점\n\n"
         "예시 — 어떤 토너 평점 4.9/5인데\n트러블/자극 속성만 보면 부정 67%\n"
         "→ 평점만 봐서는 알 수 없는 정보",
         7.1, 2.5, 5.2, 4.0, size=14, color=WHITE, line_spacing=1.4)

# ---------- Slide 6: 서비스 + 배포 + 마무리 ----------
s = add_slide(WHITE)
add_text(s, "서비스 구성 & 마무리", 0.7, 0.5, 11.5, 0.8, size=30, color=NAVY, bold=True, font="Georgia")

tabs = [
    ("🛍️ 상품 리포트", "상품 검색 → 속성별 긍정비율\n+ 대표 긍정/부정 리뷰", CORAL),
    ("🔍 리뷰 텍스트 분석", "텍스트 입력 → ML/DL 동시\n예측 + 확률 시각화", NAVY),
    ("📊 데이터 대시보드", "플랫폼/별점/트렌드/카테고리\n분포, 형태소 기반 키워드", NAVY),
]
tx = 0.7
tw = 3.85
for i, (title, desc, color) in enumerate(tabs):
    card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(tx + i*(tw+0.2)), Inches(1.6), Inches(tw), Inches(2.0))
    card.adjustments[0] = 0.08
    card.fill.solid(); card.fill.fore_color.rgb = color
    card.line.fill.background(); card.shadow.inherit = False
    add_text(s, title, tx + i*(tw+0.2) + 0.25, 1.82, tw - 0.5, 0.5, size=14.5, bold=True, color=WHITE)
    add_text(s, desc, tx + i*(tw+0.2) + 0.25, 2.35, tw - 0.5, 1.1, size=12, color=ICE, line_spacing=1.3)

add_text(s, "정리", 0.7, 3.9, 11.5, 0.4, size=16, bold=True, color=NAVY)
add_bullets(s, [
    "538,774건 데이터를 통일된 기준으로 통합 (가장 큰 난관: 라벨 기준 불일치)",
    "환경 제약을 numpy 구현 → 별도 venv 구성으로 단계적으로 해결, 4개 모델 비교",
    "실제 분포 재평가로 숨은 문제(label shift)를 찾아 보정, ABSA로 서비스를 실용적으로 전환",
    "requirements.txt·사전 집계 데이터 포함으로 재학습 없이 바로 배포 가능하게 구성",
], 0.7, 4.4, 11.5, 2.6, size=14.5)

prs.save(r"D:\crolling\BeautyScope_발표.pptx")
print("저장 완료")
