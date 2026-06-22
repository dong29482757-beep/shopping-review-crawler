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

# ---------- Slide 2: 어떤 문제를 ML/DL로 풀었나 ----------
s = add_slide(WHITE)
add_text(s, "어떤 문제를 ML/DL로 풀었나", 0.7, 0.5, 11.5, 0.8, size=30, color=NAVY, bold=True, font="Georgia")
add_bullets(s, [
    "리뷰가 상품당 수백~수천 건 — 사람이 다 읽고 판단하기 어렵다",
    "별점만 봐서는 \"왜\" 좋고 나쁜지, 속성별로(보습/향/트러블) 어떤지 알 수 없다",
], 0.7, 1.6, 5.9, 1.8, size=16)

card1 = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(3.5), Inches(5.9), Inches(3.2))
card1.adjustments[0] = 0.06
card1.fill.solid(); card1.fill.fore_color.rgb = NAVY
card1.line.fill.background(); card1.shadow.inherit = False
add_text(s, "① 감성 분류 (ML+DL)", 1.0, 3.75, 5.3, 0.5, size=17, bold=True, color=WHITE)
add_text(s, "리뷰 텍스트 → 긍정/중립/부정\nML: TF-IDF+로지스틱회귀\nDL: numpy 직접구현 신경망\n(+LSTM/Transformer 비교실험)",
         1.0, 4.3, 5.3, 2.2, size=14, color=ICE, line_spacing=1.4)

card2 = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(3.5), Inches(5.7), Inches(3.2))
card2.adjustments[0] = 0.06
card2.fill.solid(); card2.fill.fore_color.rgb = CORAL
card2.line.fill.background(); card2.shadow.inherit = False
add_text(s, "② 속성기반 감성분석 (ABSA)", 7.2, 3.75, 5.1, 0.5, size=17, bold=True, color=WHITE)
add_text(s, "리뷰를 속성별로 쪼개서 분석\n\"보습력은 좋은데 향은 별로다\"\n같은 세부 정보를 추출해\n구매 의사결정을 지원",
         7.2, 4.3, 5.1, 2.2, size=14, color=WHITE, line_spacing=1.4)

# ---------- Slide 3: 데이터 수집 — 처음엔 쿠팡만, 더 모았다 ----------
s = add_slide(WHITE)
add_text(s, "데이터 수집 — 처음엔 쿠팡만, 더 모았다", 0.7, 0.5, 11.5, 0.8, size=28, color=NAVY, bold=True, font="Georgia")

stages = [
    ("1차", "쿠팡 크롤링\n(20개 키워드)", "86,379건"),
    ("2차", "+ 무신사\n(동료 크롤링 데이터)", "230,870건"),
    ("2차", "+ 올리브영\n(JSONL 4개 파일)", "221,525건"),
    ("최종", "스키마/라벨 통일\n+ 중복 제거", "538,774건"),
]
sx = 0.7
sw = 2.85
for i, (stage, label, count) in enumerate(stages):
    color = CORAL if i == len(stages) - 1 else NAVY
    card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(sx + i*(sw+0.15)), Inches(1.7), Inches(sw), Inches(2.6))
    card.adjustments[0] = 0.08
    card.fill.solid(); card.fill.fore_color.rgb = color
    card.line.fill.background(); card.shadow.inherit = False
    add_text(s, stage, sx + i*(sw+0.15) + 0.2, 1.95, sw-0.4, 0.4, size=13, bold=True, color=ICE)
    add_text(s, label, sx + i*(sw+0.15) + 0.2, 2.4, sw-0.4, 1.0, size=14, bold=True, color=WHITE, line_spacing=1.25)
    add_text(s, count, sx + i*(sw+0.15) + 0.2, 3.55, sw-0.4, 0.6, size=20, bold=True, color=WHITE)
    if i < len(stages) - 1:
        arrow_x = sx + i*(sw+0.15) + sw + 0.01
        arr = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(arrow_x), Inches(2.85), Inches(0.13), Inches(0.3))
        arr.fill.solid(); arr.fill.fore_color.rgb = GREY
        arr.line.fill.background(); arr.shadow.inherit = False

add_text(s, "데이터 장점", 0.7, 4.7, 5.6, 0.4, size=16, bold=True, color=NAVY)
add_bullets(s, [
    "별점 기반 라벨이 이미 존재 → 별도 수작업 레이블링 불필요",
    "화장품 도메인 특화, 2015~2026년 10년치 데이터",
    "20개+ 카테고리로 비교 분석 용이",
], 0.7, 5.2, 5.6, 1.8, size=13.5)

add_text(s, "최종 분포", 6.8, 4.7, 5.9, 0.4, size=16, bold=True, color=NAVY)
chart_data = CategoryChartData()
chart_data.categories = ["쿠팡", "무신사", "올리브영"]
chart_data.add_series("건수", (86379, 230870, 221525))
gframe = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(6.8), Inches(5.1), Inches(5.9), Inches(1.9), chart_data)
chart = gframe.chart
chart.has_legend = False
chart.plots[0].series[0].format.fill.solid()
chart.plots[0].series[0].format.fill.fore_color.rgb = NAVY

# ---------- Slide 4: 데이터 준비의 어려움 ----------
s = add_slide(WHITE)
add_text(s, "데이터 준비 — 가장 까다로웠던 단계", 0.7, 0.5, 11.5, 0.8, size=28, color=NAVY, bold=True, font="Georgia")

issues = [
    ("스키마 불일치", "쿠팡/무신사/올리브영 컬럼명이 전부 다름",
     "플랫폼별 로더로 공통 스키마 변환 후 병합"),
    ("라벨 기준 불일치 (핵심)", "무신사 sentiment가 별점 아닌 텍스트분석 기반 → 5점 리뷰의 21%가 '부정'",
     "전체 데이터의 sentiment를 별점에서 일괄 재계산"),
    ("인코딩 깨짐", "무신사 CSV 기본 인코딩으로 읽으면 한글 깨짐",
     "encoding='utf-8-sig' 명시"),
    ("클래스 불균형", "긍정 86.7% — 그대로 학습하면 다 긍정 찍어도 86%",
     "부정/중립 전량 + 긍정은 2배 규모로만 다운샘플링"),
    ("불용어/형태소 미처리", "정규식으로만 잘라서 조사가 토큰에 섞임",
     "Okt 형태소분석 + 어간정규화 + 불용어 제거"),
]
y = 1.5
for title, problem, solution in issues:
    card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(y), Inches(11.9), Inches(1.04))
    card.adjustments[0] = 0.08
    card.fill.solid(); card.fill.fore_color.rgb = RGBColor(0xF4, 0xF6, 0xFC)
    card.line.fill.background(); card.shadow.inherit = False
    add_chip(s, title, 0.92, y + 0.15, 2.65, 0.42, CORAL, size=11.5)
    add_text(s, problem, 3.75, y + 0.08, 4.0, 0.88, size=11.5, color=GREY, line_spacing=1.15)
    add_text(s, "해결 → " + solution, 7.9, y + 0.08, 4.55, 0.88, size=11.5, color=NAVY, bold=True, line_spacing=1.15)
    y += 1.14

# ---------- Slide 5: AI(Claude Code) 활용 ----------
s = add_slide(NAVY)
add_text(s, "AI(Claude Code)로 어떻게 구현했나", 0.7, 0.5, 11.5, 0.8, size=28, color=WHITE, bold=True, font="Georgia")
add_bullets(s, [
    "전처리·모델·Streamlit 앱 코드를 페어 프로그래밍 방식으로 작성",
    "라벨 불일치를 \"느낌\"이 아니라 crosstab 코드를 직접 돌려 수치로 진단",
    "막힐 때마다(PyTorch 미설치 등) 대안을 같이 설계하고 바로 실행",
    "모델을 만들고 끝내지 않고, 실제 분포로 재평가해서 숨은 문제를 찾아냄",
], 0.7, 1.6, 6.1, 3.3, size=15.5, color=WHITE)

box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.1), Inches(1.5), Inches(5.6), Inches(5.3))
box.adjustments[0] = 0.04
box.fill.solid(); box.fill.fore_color.rgb = RGBColor(0x28, 0x33, 0x70)
box.line.fill.background(); box.shadow.inherit = False
add_text(s, "예상치 못한 벽: PyTorch 설치 실패", 7.5, 1.8, 4.8, 0.6, size=16, bold=True, color=CORAL)
add_text(s,
         "환경의 Python이 3.14라서 PyTorch/TensorFlow\n휠이 아직 배포되지 않음\n"
         "→ pip install torch: No matching distribution\n\n"
         "1단계 해결: numpy로 신경망 직접 구현\n"
         "2단계 해결: winget으로 Python 3.11을 따로\n설치해 별도 venv 구성 → 실제 PyTorch\nLSTM/Transformer까지 검증",
         7.5, 2.5, 4.8, 4.0, size=13.5, color=WHITE, line_spacing=1.4)

# ---------- Slide 6: DL 모델 — numpy 신경망 구성 ----------
s = add_slide(WHITE)
add_text(s, "DL 모델 — numpy로 직접 구현한 신경망", 0.7, 0.5, 11.5, 0.8, size=26, color=NAVY, bold=True, font="Georgia")

layers = [("입력\nTF-IDF(형태소)\n15,000차원", ICE),
          ("Dense 128\nReLU", NAVY),
          ("Dense 64\nReLU", NAVY),
          ("Dense 3\nSoftmax", CORAL)]
lx = 0.9
lw = 2.55
ly = 1.6
lh = 1.6
for i, (label, color) in enumerate(layers):
    shp = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(lx + i*(lw+0.4)), Inches(ly), Inches(lw), Inches(lh))
    shp.adjustments[0] = 0.08
    shp.fill.solid(); shp.fill.fore_color.rgb = color
    shp.line.fill.background(); shp.shadow.inherit = False
    tcolor = NAVY if color == ICE else WHITE
    tf = shp.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    for j, line in enumerate(label.split("\n")):
        pp = p if j == 0 else tf.add_paragraph()
        pp.alignment = PP_ALIGN.CENTER
        r = pp.add_run(); r.text = line
        r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = tcolor
    if i < len(layers) - 1:
        arrow_x = lx + i*(lw+0.4) + lw + 0.02
        arr = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(arrow_x), Inches(ly + lh/2 - 0.12), Inches(0.36), Inches(0.24))
        arr.fill.solid(); arr.fill.fore_color.rgb = GREY
        arr.line.fill.background(); arr.shadow.inherit = False

add_text(s, "학습 방식", 0.9, 3.6, 5.6, 0.4, size=15, bold=True, color=NAVY)
add_bullets(s, [
    "Mini-batch SGD + Momentum(0.9), L2 정규화",
    "learning rate 0.08 → epoch마다 0.92배 감소",
    "batch size 256, 15 epoch",
    "scipy sparse(TF-IDF) × dense 가중치 행렬곱을\nbackprop 수식에 맞춰 직접 구현",
], 0.9, 4.05, 5.6, 2.8, size=13)

add_text(s, "추가 실험 (별도 venv, PyTorch)", 6.9, 3.6, 5.6, 0.4, size=15, bold=True, color=NAVY)
add_bullets(s, [
    "LSTM: Embedding → BiLSTM(128) → Dense(3)",
    "KoELECTRA-small 파인튜닝 (사전학습 모델)",
    "winget으로 Python 3.11 별도 설치 후 venv 구성",
], 6.9, 4.05, 5.6, 1.8, size=13)
box2 = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(5.5), Inches(5.6), Inches(1.5))
box2.adjustments[0]=0.08
box2.fill.solid(); box2.fill.fore_color.rgb = RGBColor(0xF4,0xF6,0xFC)
box2.line.fill.background(); box2.shadow.inherit = False
add_text(s, "관찰: LSTM이 순서 정보를 학습할 수 있는데도\nTF-IDF 기반 모델과 성능이 비슷함 — 짧은 리뷰는\n어휘 자체가 이미 강한 신호였다는 뜻",
         7.1, 5.65, 5.2, 1.3, size=12, color=GREY, line_spacing=1.25)

# ---------- Slide 7: 4개 모델 비교 ----------
s = add_slide(WHITE)
add_text(s, "4개 모델 비교", 0.7, 0.5, 8, 0.8, size=30, color=NAVY, bold=True, font="Georgia")

chart_data2 = CategoryChartData()
chart_data2.categories = ["ML\n(TF-IDF+LogReg)", "DL\n(numpy FFNN)", "LSTM\n(PyTorch)", "KoELECTRA\n(파인튜닝)"]
chart_data2.add_series("accuracy", (0.730, 0.754, 0.734, 0.772))
chart_data2.add_series("macro F1", (0.668, 0.664, 0.671, 0.660))
gframe2 = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.7), Inches(1.6), Inches(7.6), Inches(4.3), chart_data2)
chart2 = gframe2.chart
chart2.has_legend = True
chart2.legend.position = XL_LEGEND_POSITION.BOTTOM
chart2.legend.include_in_layout = False
chart2.plots[0].series[0].format.fill.solid()
chart2.plots[0].series[0].format.fill.fore_color.rgb = NAVY
chart2.plots[0].series[1].format.fill.solid()
chart2.plots[0].series[1].format.fill.fore_color.rgb = CORAL

add_text(s, "결론", 8.6, 1.7, 4.2, 0.4, size=16, bold=True, color=NAVY)
add_bullets(s, [
    "KoELECTRA가 데이터 1/7만 쓰고도\n최고 accuracy → 사전학습 효과 확인",
    "LSTM은 순서 정보 활용 기대했으나\n차이 없음 (학습 데이터 규모 한계)",
    "구조보다 어휘 신호 자체가 강한\n도메인이라는 결론",
], 8.6, 2.2, 4.2, 3.2, size=13)

note = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(6.1), Inches(11.9), Inches(0.8))
note.adjustments[0]=0.1
note.fill.solid(); note.fill.fore_color.rgb = RGBColor(0xF4,0xF6,0xFC)
note.line.fill.background(); note.shadow.inherit = False
add_text(s, "KoELECTRA: 20,000건 서브샘플 · 2 epoch (CPU 환경 시간 제약, GPU면 격차 더 벌어질 것으로 예상)",
         1.0, 6.3, 11.3, 0.4, size=12.5, color=GREY, align=PP_ALIGN.CENTER)

# ---------- Slide 8: 모델 문제점 발견과 보정 ----------
s = add_slide(WHITE)
add_text(s, "모델 문제점 발견 — 실제 분포로 재평가", 0.7, 0.5, 11.5, 0.8, size=28, color=NAVY, bold=True, font="Georgia")
add_bullets(s, [
    "학습 시 클래스 밸런싱(다운샘플링)을 했는데, 실제 운영 비율(positive 86.7%)과 다름",
    "실제 분포 샘플로 재평가하니 neutral precision이 0.20까지 떨어짐",
    "= 모델이 \"중립\"이라고 예측한 것 중 80%가 틀림 (label shift 문제)",
], 0.7, 1.6, 11.5, 2.0, size=15.5)

box3 = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(3.5), Inches(11.9), Inches(0.9))
box3.adjustments[0]=0.1
box3.fill.solid(); box3.fill.fore_color.rgb = CORAL
box3.line.fill.background(); box3.shadow.inherit = False
add_text(s, "해결: p_real(y|x) ∝ p_model(y|x) × (실제 클래스 비율 / 학습 클래스 비율) — 재학습 없이 추론 단계에서 확률 보정",
         1.0, 3.75, 11.3, 0.5, size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

chart_data3 = CategoryChartData()
chart_data3.categories = ["ML accuracy", "ML macro F1", "DL accuracy", "DL macro F1"]
chart_data3.add_series("보정 전", (0.806, 0.626, 0.890, 0.712))
chart_data3.add_series("보정 후", (0.909, 0.675, 0.920, 0.711))
gframe3 = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(1.5), Inches(4.7), Inches(10.3), Inches(2.5), chart_data3)
chart3 = gframe3.chart
chart3.has_legend = True
chart3.legend.position = XL_LEGEND_POSITION.BOTTOM
chart3.legend.include_in_layout = False
chart3.plots[0].series[0].format.fill.solid()
chart3.plots[0].series[0].format.fill.fore_color.rgb = GREY
chart3.plots[0].series[1].format.fill.solid()
chart3.plots[0].series[1].format.fill.fore_color.rgb = NAVY

# ---------- Slide 9: 서비스 피드백 — ABSA 상품 리포트로 전환 ----------
s = add_slide(NAVY)
add_text(s, "\"서비스가 실용성이 없다\" — 피드백과 전환", 0.7, 0.5, 11.5, 0.8, size=27, color=WHITE, bold=True, font="Georgia")
add_bullets(s, [
    "기존: 리뷰 텍스트를 입력하면 감성을 알려주는 데모",
    "문제: 이미 써본 리뷰를 사람이 직접 타이핑할 이유가 없음 — 실용성 없음",
    "전환: \"상품 리포트\" — 상품 검색 → 속성별(8개) 장단점 + 대표 리뷰",
], 0.7, 1.6, 6.1, 2.6, size=15.5, color=WHITE)

box4 = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.1), Inches(1.5), Inches(5.6), Inches(5.3))
box4.adjustments[0] = 0.04
box4.fill.solid(); box4.fill.fore_color.rgb = RGBColor(0x28, 0x33, 0x70)
box4.line.fill.background(); box4.shadow.inherit = False
add_text(s, "실제 발견한 예시", 7.5, 1.8, 4.8, 0.5, size=16, bold=True, color=CORAL)
add_text(s,
         "어떤 토너의 전체 평점: 4.9 / 5 (거의 만점)\n\n"
         "하지만 속성별로 쪼개보면—\n"
         "보습/수분: 긍정 85%\n가격/가성비: 긍정 96%\n트러블/자극: 긍정 33% (부정 67%)\n\n"
         "→ 평점만 봐서는 절대 알 수 없는 정보",
         7.5, 2.5, 4.8, 4.0, size=14.5, color=WHITE, line_spacing=1.5)

add_text(s, "538,774건 전체를 52초에 처리 (규칙 기반 속성분석, absa.py — ML 전체 적용은 Okt 병목으로 비용이 너무 커서 정규식 매칭으로 대체)",
         0.7, 4.5, 6.1, 1.8, size=12.5, color=ICE, line_spacing=1.4)

# ---------- Slide 10: Streamlit 서비스 구성 ----------
s = add_slide(WHITE)
add_text(s, "Streamlit 서비스 — BeautyScope", 0.7, 0.5, 11.5, 0.8, size=29, color=NAVY, bold=True, font="Georgia")

tabs = [
    ("🛍️ 상품 리포트", "상품 검색 → 속성별 긍정비율\n+ 대표 긍정/부정 리뷰", CORAL),
    ("🔍 리뷰 텍스트 분석", "텍스트 입력 → ML/DL 동시\n예측 + 확률 시각화", NAVY),
    ("📊 데이터 대시보드", "플랫폼/별점/트렌드/카테고리\n분포, 형태소 기반 키워드", NAVY),
]
tx = 0.7
tw = 3.85
for i, (title, desc, color) in enumerate(tabs):
    card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(tx + i*(tw+0.2)), Inches(1.7), Inches(tw), Inches(2.3))
    card.adjustments[0] = 0.08
    card.fill.solid(); card.fill.fore_color.rgb = color
    card.line.fill.background(); card.shadow.inherit = False
    add_text(s, title, tx + i*(tw+0.2) + 0.25, 1.95, tw - 0.5, 0.5, size=15, bold=True, color=WHITE)
    add_text(s, desc, tx + i*(tw+0.2) + 0.25, 2.55, tw - 0.5, 1.2, size=12.5, color=ICE, line_spacing=1.3)

add_text(s, "동작 확인", 0.7, 4.3, 11.5, 0.4, size=16, bold=True, color=NAVY)
add_bullets(s, [
    "로컬 환경에서 streamlit run app.py 실행 → HTTP 200 응답 확인",
    "상품 검색 → 속성별 긍정비율/대표리뷰 정상 출력 확인",
    "리뷰 텍스트 입력 → ML/DL 예측 일치 확인 (긍정/부정 예시 모두 정답)",
], 0.7, 4.8, 11.5, 1.8, size=14)

# ---------- Slide 11: 배포 준비 ----------
s = add_slide(WHITE)
add_text(s, "배포 준비", 0.7, 0.5, 8, 0.8, size=32, color=NAVY, bold=True, font="Georgia")
add_bullets(s, [
    "requirements.txt로 의존성 고정 (scikit-learn, streamlit, pandas, numpy, scipy, joblib, konlpy)",
    "학습된 모델 + 집계 데이터를 models/에 포함 → 재학습 없이 바로 서비스 구동 가능",
    "538,774건 원본 대신 사전 집계 CSV(대시보드/상품리포트용)를 서비스가 읽도록 분리",
    "대용량 원본 크롤링 CSV는 .gitignore 처리, 정제된 데이터/모델/집계 파일만 추적",
], 0.7, 1.7, 11.5, 3.5, size=16)

box5 = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(5.5), Inches(11.9), Inches(1.3))
box5.adjustments[0]=0.08
box5.fill.solid(); box5.fill.fore_color.rgb = RGBColor(0xF4,0xF6,0xFC)
box5.line.fill.background(); box5.shadow.inherit = False
add_text(s, "다음 과제: 대용량 데이터 Git LFS/외부 스토리지 연동, ABSA 정확도를 ML 분류기로\n고도화(현재는 규칙 기반), GPU 환경에서 KoELECTRA 전체 데이터 파인튜닝",
         1.0, 5.75, 11.3, 0.9, size=14, color=GREY, line_spacing=1.3)

# ---------- Slide 12: 마무리 ----------
s = add_slide(NAVY)
add_text(s, "정리", 1, 1.0, 11.3, 0.8, size=36, color=WHITE, bold=True, font="Georgia")
add_bullets(s, [
    "3개 플랫폼 538,774건 데이터를 통일된 기준으로 통합 (가장 큰 난관: 라벨 기준 불일치)",
    "환경 제약(PyTorch 미설치)을 numpy 구현 → 별도 venv 구성으로 2단계에 걸쳐 해결",
    "ML/DL/LSTM/Transformer 4개 모델을 비교하고, 실제 분포 재평가로 숨은 문제(label shift)를 찾아 보정",
    "\"실용성 없다\"는 피드백을 받고 텍스트 데모 → 속성기반 상품 리포트로 서비스 자체를 전환",
    "Streamlit으로 서비스를 구현하고 동작까지 검증",
], 1, 2.0, 11.0, 4.2, size=16.5, color=WHITE)
add_text(s, "BeautyScope", 1, 6.5, 11.3, 0.6, size=20, color=CORAL, bold=True, font="Georgia")

prs.save(r"D:\crolling\BeautyScope_발표.pptx")
print("저장 완료")
