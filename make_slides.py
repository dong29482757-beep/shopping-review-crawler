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

# ---------- Slide 3: 쿠팡 크롤링 — 봇 탐지를 어떻게 뚫었나 ----------
s = add_slide(NAVY)
add_text(s, "쿠팡 크롤링 — 봇 탐지를 어떻게 뚫었나", 0.7, 0.5, 11.5, 0.8, size=27, color=WHITE, bold=True, font="Georgia")
add_text(s, "쿠팡은 문지기(Akamai)가 \"이 손님이 사람인지 로봇인지\" 5단계로 검사한다", 0.7, 1.35, 11.5, 0.5,
         size=14.5, color=ICE, italic=True)

box1 = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(2.0), Inches(5.8), Inches(4.6))
box1.adjustments[0] = 0.05
box1.fill.solid(); box1.fill.fore_color.rgb = RGBColor(0x28, 0x33, 0x70)
box1.line.fill.background(); box1.shadow.inherit = False
add_text(s, "왜 막혔나", 1.0, 2.3, 5.1, 0.5, size=17, bold=True, color=CORAL)
add_bullets(s, [
    "requests로 접속 → 헤더만 보고 1단계에서 바로 차단",
    "Selenium으로 접속 → \"자동화 도구\" 흔적이 들켜서\n3단계에서 차단",
    "마우스·스크롤 없이 너무 빠르게 요청하면\n행동 패턴에서 차단",
], 1.0, 2.9, 5.2, 3.5, size=14, color=WHITE, space_after=14)

box2 = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(2.0), Inches(5.8), Inches(4.6))
box2.adjustments[0] = 0.05
box2.fill.solid(); box2.fill.fore_color.rgb = CORAL
box2.line.fill.background(); box2.shadow.inherit = False
add_text(s, "어떻게 뚫었나 — \"진짜 손님\" 행세", 7.1, 2.3, 5.2, 0.5, size=17, bold=True, color=WHITE)
add_bullets(s, [
    "가짜 브라우저 대신, 내 컴퓨터의 실제 Chrome을\n그대로 원격 연결해서 사용 (Playwright + CDP)",
    "검색창에 키워드를 한 글자씩 타이핑\n(URL로 바로 안 들어감)",
    "상품 사이 랜덤 대기, 가끔 쿠팡 홈으로 돌아가\n쉬기 — 사람처럼 행동",
], 7.1, 2.9, 5.2, 3.5, color=WHITE, size=14, space_after=14)

add_text(s, "핵심: 자동화 도구를 \"새로 띄우는\" 게 아니라, 이미 로그인된 실제 브라우저에 \"숟가락만 얹는\" 방식이라 자동화 흔적 자체가 없다",
         0.7, 6.75, 11.9, 0.5, size=12.5, color=ICE, italic=True, align=PP_ALIGN.CENTER)

# ---------- Slide 4: 데이터 준비 — 가장 까다로웠던 단계 ----------
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

# ---------- Slide 5: AI 활용 + 모델 비교 ----------
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

# ---------- Slide 6: 모델 문제 발견 & 보정 ----------
s = add_slide(NAVY)
add_text(s, "모델 문제 발견 — 실제 분포로 재평가", 0.7, 0.5, 11.5, 0.8, size=27, color=WHITE, bold=True, font="Georgia")

add_bullets(s, [
    "학습 시 클래스 밸런싱(다운샘플링)을 했는데, 실제 운영 비율(positive 86.7%)과 다름",
    "실제 분포 샘플로 재평가하니 neutral precision이 0.20까지 하락 (label shift)",
    "= 모델이 \"중립\"이라고 예측한 것 중 80%가 틀림",
], 0.7, 1.7, 11.5, 2.0, size=16, color=WHITE)

box3 = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(3.6), Inches(11.9), Inches(0.9))
box3.adjustments[0] = 0.1
box3.fill.solid(); box3.fill.fore_color.rgb = CORAL
box3.line.fill.background(); box3.shadow.inherit = False
add_text(s, "해결: 재학습 없이 추론 단계에서 확률 보정 (학습 비율 ↔ 실제 비율 차이로 보정)",
         1.0, 3.85, 11.3, 0.5, size=15, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

chart_data3 = CategoryChartData()
chart_data3.categories = ["ML accuracy", "ML macro F1", "DL accuracy", "DL macro F1"]
chart_data3.add_series("보정 전", (0.806, 0.626, 0.890, 0.712))
chart_data3.add_series("보정 후", (0.909, 0.675, 0.920, 0.711))
gframe3 = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(1.8), Inches(4.7), Inches(9.7), Inches(2.4), chart_data3)
chart3 = gframe3.chart
chart3.has_legend = True
chart3.legend.position = XL_LEGEND_POSITION.BOTTOM
chart3.legend.include_in_layout = False
chart3.plots[0].series[0].format.fill.solid()
chart3.plots[0].series[0].format.fill.fore_color.rgb = RGBColor(0x8A, 0x90, 0xA8)
chart3.plots[0].series[1].format.fill.solid()
chart3.plots[0].series[1].format.fill.fore_color.rgb = CORAL

# ---------- Slide 7: 서비스 진화 & 마무리 ----------
s = add_slide(WHITE)
add_text(s, "서비스 진화 — 텍스트 데모에서 실용적 리포트로", 0.7, 0.5, 11.5, 0.8, size=24, color=NAVY, bold=True, font="Georgia")

steps = [
    ("1차", "리뷰 텍스트를 직접\n타이핑하는 데모", "→ \"실용성 없다\" 피드백", GREY),
    ("2차", "상품 검색 → 8개 속성별\n긍정비율 + 대표리뷰", "→ \"더 구체적이면 좋겠다\"", NAVY),
    ("3차\n(현재)", "+ 속성별 랭킹\n+ 대안 상품 추천\n+ 피부타입별 세그먼트", "구매 의사결정까지 지원", CORAL),
]
sx = 0.7
sw = 3.85
for i, (stage, desc, note, color) in enumerate(steps):
    card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(sx + i*(sw+0.2)), Inches(1.6), Inches(sw), Inches(2.7))
    card.adjustments[0] = 0.07
    card.fill.solid(); card.fill.fore_color.rgb = color
    card.line.fill.background(); card.shadow.inherit = False
    add_text(s, stage, sx + i*(sw+0.2) + 0.25, 1.8, sw - 0.5, 0.4, size=13, bold=True, color=ICE)
    add_text(s, desc, sx + i*(sw+0.2) + 0.25, 2.25, sw - 0.5, 1.3, size=13, bold=True, color=WHITE, line_spacing=1.3)
    add_text(s, note, sx + i*(sw+0.2) + 0.25, 3.65, sw - 0.5, 0.55, size=11.5, color=ICE, italic=True, line_spacing=1.2)
    if i < len(steps) - 1:
        arrow_x = sx + i*(sw+0.2) + sw + 0.02
        arr = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(arrow_x), Inches(2.8), Inches(0.16), Inches(0.35))
        arr.fill.solid(); arr.fill.fore_color.rgb = GREY
        arr.line.fill.background(); arr.shadow.inherit = False

add_text(s, "예: 트러블 잘 올라오는 상품 → 같은 카테고리에서 트러블 평가 좋은 대안을 바로 추천 / 건성·지성·복합성·민감성 피부별로 평가가 따로 보임",
         0.7, 4.55, 11.9, 0.6, size=12.5, color=GREY, italic=True)

add_text(s, "정리", 0.7, 5.3, 11.5, 0.4, size=16, bold=True, color=NAVY)
add_bullets(s, [
    "538,774건 데이터를 통일된 기준으로 통합, 4개 모델(ML/DL/LSTM/Transformer)을 비교 학습",
    "실제 분포 재평가로 숨은 문제(label shift)를 찾아 보정, 두 차례 피드백으로 서비스를 실용적으로 발전",
], 0.7, 5.8, 11.5, 1.3, size=14)

prs.save(r"D:\crolling\BeautyScope_발표.pptx")
print("저장 완료")
