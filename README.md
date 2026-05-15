# 쇼핑몰 리뷰 크롤러

쇼핑몰 리뷰 데이터를 수집해서 텍스트 분석에 활용하는 프로젝트입니다.  
나중에 GS샵, CJ온스타일 등 다른 홈쇼핑 사이트로도 확장할 예정입니다.

---

## 수집 현황

| 사이트 | 키워드 수 | 상품 수 | 리뷰 수 | 수집일 |
|--------|-----------|---------|---------|--------|
| 쿠팡 | 20개 | 545개 | 108,022건 | 2026-05-14 |

### 쿠팡 키워드 목록
화장품, 스킨케어, 마스크팩, 선크림, 토너, 세럼, 클렌징폼, 파운데이션, 립스틱, 아이크림,  
BB크림, 쿠션팩트, 컨실러, 수분크림, 클렌징오일, 립틴트, 아이섀도, 마스카라, 나이트크림, 미스트

### 별점 분포 (쿠팡)
| 별점 | 건수 | 비율 |
|------|------|------|
| 1점 | 6,392건 | 5.9% |
| 2점 | 1,994건 | 1.8% |
| 3점 | 2,490건 | 2.3% |
| 4점 | 8,077건 | 7.5% |
| 5점 | 89,069건 | 82.5% |

---

## 기술 스택

- Python 3.14
- Playwright (브라우저 자동화)
- BeautifulSoup4 (HTML 파싱)
- pandas, tqdm

---

## 쿠팡 차단 우회 방법

쿠팡은 **Akamai Bot Manager**라는 봇 탐지 시스템을 쓰고 있어서 일반적인 requests나 Selenium으로는 바로 차단됩니다. 몇 가지 시도 끝에 아래 방식으로 뚫었습니다.

### 왜 일반 방식이 안 되냐

Akamai는 크게 5단계로 봇을 탐지합니다.

1. HTTP 헤더, TLS 지문 분석
2. `_abck` 쿠키 기반 세션 검증
3. `navigator.webdriver` 등 브라우저 자동화 흔적 탐지
4. 마우스/키보드/스크롤 패턴 분석
5. IP 평판, 요청 빈도

requests는 1단계부터 막히고, Selenium도 3단계에서 걸립니다.

### 해결 방법: 실제 Chrome + CDP 연결

핵심은 **진짜 Chrome을 띄워서 Playwright가 CDP로 붙는 것**입니다.

```
실제 Chrome 실행 (원격 디버깅 포트 오픈)
       ↓
Playwright가 CDP(Chrome DevTools Protocol)로 연결
       ↓
이미 로그인된 쿠키를 임시 프로필에 복사해서 사용
       ↓
검색창에 키워드를 직접 타이핑 (URL 직접 접속 X)
```

- `--remote-debugging-port=9222`로 Chrome 실행
- 실제 Chrome 프로필의 쿠키(`Cookies`, `Local State`)를 임시 폴더에 복사
- Playwright의 `connect_over_cdp()`로 연결
- 검색은 URL 직접 접속 대신 검색창에 한 글자씩 타이핑

### 리뷰 데이터 수집 방법

리뷰 페이지를 직접 긁는 게 아니라, 브라우저가 내부적으로 호출하는 **API 응답을 가로채는 방식**을 씁니다.

```
상품 페이지 접속 → 상품평 탭 클릭
       ↓
브라우저가 내부 API 자동 호출
https://www.coupang.com/next-api/review?productId=...
       ↓
Playwright response interceptor로 JSON 응답 캡처
       ↓
rData → paging → contents 경로로 리뷰 목록 추출
```

2페이지부터는 `page.request.get()`으로 직접 호출합니다.  
별점 필터(`ratings=1`, `ratings=2`)를 따로 요청해서 낮은 별점 리뷰도 일정 수 이상 확보했습니다.

### 차단 방지를 위한 장치

- 상품 사이 랜덤 딜레이 (2~4초)
- 상품 5개마다 쿠팡 홈 방문 + 15~30초 휴식
- 키워드 전환마다 1~2분 대기
- 랜덤 스크롤로 사람처럼 행동

---

## 파일 구조

```
crolling/
├── coupang_crawler.py   # 메인 크롤러 클래스
├── run_test.py          # 테스트용 (상품 1개, 리뷰 30건)
├── run_full.py          # 본격 수집
├── run_more.py          # 추가 수집 (기존 상품 중복 제외)
└── README.md
```

---

## 실행 방법

```bash
# 가상환경 활성화
.\coupang_env\Scripts\activate

# 테스트 실행 (Chrome 완전히 닫은 상태에서)
python run_test.py

# 본격 수집
python run_full.py
```

> Chrome을 완전히 종료한 상태에서 실행해야 합니다.  
> 실행하면 Chrome이 자동으로 뜨고 크롤링이 시작됩니다.
