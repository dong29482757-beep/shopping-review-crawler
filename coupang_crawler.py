"""
쿠팡 화장품 리뷰 크롤러 (2026)
- Chrome을 먼저 일반 모드로 띄운 뒤 Playwright가 CDP로 연결
- Akamai 자동화 탐지 우회
- 실행 전 Chrome을 완전히 닫아두세요
"""

import time
import random
import re
import subprocess
import shutil
import tempfile
import os
import pandas as pd
from datetime import datetime
from tqdm import tqdm
from bs4 import BeautifulSoup

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout


CHROME_PATH    = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CHROME_PROFILE = r"C:\Users\user\AppData\Local\Google\Chrome\User Data"
CDP_PORT       = 9222
REVIEW_URL = (
    "https://www.coupang.com/next-api/review"
    "?productId={pid}&page={page}&size=10&sortBy=ORDER_SCORE_ASC&ratingSummary=true"
)
REVIEW_URL_RATING = (
    "https://www.coupang.com/next-api/review"
    "?productId={pid}&page={page}&size=10&sortBy=ORDER_SCORE_ASC&ratingSummary=true&ratings={rating}"
)


class CoupangCrawler:

    def __init__(self, headless=False):
        self.headless       = headless
        self._chrome_proc   = None
        self._tmp_profile   = None
        self._pw            = None
        self._browser       = None
        self._page          = None

    # ── 브라우저 시작 / 종료 ───────────────────────────────────────────
    def start(self):
        # 기존 Chrome 프로세스 강제 종료
        subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)
        time.sleep(3)

        # 임시 프로필 생성 후 실제 프로필 쿠키 복사
        # (Chrome은 기본 프로필로 원격 디버깅 불가 → 임시 폴더 필수)
        self._tmp_profile = tempfile.mkdtemp(prefix="coupang_chrome_")
        tmp_default = os.path.join(self._tmp_profile, "Default")
        os.makedirs(tmp_default, exist_ok=True)

        real_default = os.path.join(CHROME_PROFILE, "Default")
        # 쿠키 + 암호화 키(Local State) 복사
        for fname in ["Cookies", "Cookies-journal"]:
            src = os.path.join(real_default, fname)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(tmp_default, fname))
        local_state_src = os.path.join(CHROME_PROFILE, "Local State")
        if os.path.exists(local_state_src):
            shutil.copy2(local_state_src, os.path.join(self._tmp_profile, "Local State"))
        print(f"  임시 프로필 생성: {self._tmp_profile}")

        # Chrome 실행 (임시 프로필 + 원격 디버깅 포트)
        cmd = (
            f'"{CHROME_PATH}" '
            f"--remote-debugging-port={CDP_PORT} "
            f'--user-data-dir="{self._tmp_profile}" '
            f"--no-first-run --no-default-browser-check --window-size=1920,1080"
        )
        self._chrome_proc = subprocess.Popen(cmd, shell=True)
        print("Chrome 시작 중...")
        time.sleep(3)  # Chrome 초기 로딩 대기
        # CDP 포트가 열릴 때까지 대기
        for i in range(20):
            time.sleep(1)
            try:
                import urllib.request
                urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json/version", timeout=2)
                print(f"  Chrome CDP 포트 확인 완료 ({i+1}초)")
                break
            except Exception:
                print(f"  대기 중... ({i+1}초)")
        else:
            raise RuntimeError("Chrome CDP 포트가 열리지 않았습니다. 작업관리자에서 chrome.exe 프로세스를 모두 종료 후 재시도하세요.")

        # Playwright가 이미 떠 있는 Chrome에 CDP로 연결 (IPv4 명시)
        self._pw      = sync_playwright().start()
        self._browser = self._pw.chromium.connect_over_cdp(f"http://127.0.0.1:{CDP_PORT}")

        ctx = self._browser.contexts[0] if self._browser.contexts else self._browser.new_context(
            locale="ko-KR",
            timezone_id="Asia/Seoul",
        )
        pages = ctx.pages
        self._page = pages[0] if pages else ctx.new_page()

        print("쿠팡 홈 접속 중...")
        self._goto("https://www.coupang.com", wait_ms=4000)
        self._random_scroll()

    def stop(self):
        if self._browser:
            try:
                self._browser.close()
            except Exception:
                pass
        if self._pw:
            self._pw.stop()
        if self._chrome_proc:
            self._chrome_proc.terminate()
        if self._tmp_profile and os.path.exists(self._tmp_profile):
            shutil.rmtree(self._tmp_profile, ignore_errors=True)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *_):
        self.stop()

    # ── 내부 헬퍼 ─────────────────────────────────────────────────────
    def _goto(self, url, wait_ms=2000):
        try:
            self._page.goto(url, wait_until="domcontentloaded", timeout=30000)
        except PWTimeout:
            pass
        time.sleep(wait_ms / 1000 + random.uniform(0.2, 0.6))

    def _soup(self):
        return BeautifulSoup(self._page.content(), "html.parser")

    def _is_blocked(self):
        return "access denied" in self._page.content().lower()

    def _random_scroll(self):
        for _ in range(random.randint(2, 4)):
            self._page.mouse.wheel(0, random.randint(200, 600))
            time.sleep(random.uniform(0.3, 0.7))

    def _human_type(self, selector, text):
        self._page.click(selector)
        time.sleep(random.uniform(0.3, 0.6))
        for char in text:
            self._page.keyboard.type(char, delay=random.randint(80, 200))

    # ── 키워드 검색 ───────────────────────────────────────────────────
    def _search(self, keyword):
        search_selectors = [
            "input#headerSearchInputBox",
            "input[name='q']",
            "input[placeholder*='검색']",
            "input.search-input",
        ]
        found = None
        for sel in search_selectors:
            try:
                self._page.wait_for_selector(sel, timeout=5000)
                found = sel
                break
            except PWTimeout:
                continue

        if not found:
            print("  검색창 못 찾음 → URL 방식으로 시도")
            self._goto(
                f"https://www.coupang.com/np/search?q={keyword}&channel=user&sorter=scoreDesc&listSize=36",
                wait_ms=4000,
            )
            return

        self._human_type(found, keyword)
        time.sleep(random.uniform(0.3, 0.5))
        self._page.keyboard.press("Enter")
        time.sleep(random.uniform(3.0, 4.5))
        self._random_scroll()

    # ── 상품 목록 수집 ─────────────────────────────────────────────────
    def get_product_list(self, keyword, max_products=50):
        products = []
        print(f"\n[상품 수집] 키워드: '{keyword}', 목표: {max_products}개")

        self._search(keyword)

        if self._is_blocked():
            print("  ❌ Access Denied. Chrome을 완전히 닫고 다시 실행해보세요.")
            return products

        page_num = 1
        while len(products) < max_products:
            if page_num > 1:
                self._goto(
                    f"https://www.coupang.com/np/search?q={keyword}"
                    f"&channel=user&sorter=scoreDesc&listSize=36&page={page_num}",
                    wait_ms=3000,
                )
                self._random_scroll()

            if self._is_blocked():
                print(f"  ❌ {page_num}페이지 차단됨")
                break

            soup  = self._soup()
            links = soup.select("a[href*='/vp/products/']")
            seen  = {p["product_id"] for p in products}
            added = 0

            for a in links:
                if len(products) >= max_products:
                    break
                href = a.get("href", "")
                m = re.search(r"/vp/products/(\d+)", href)
                if not m:
                    continue
                pid = m.group(1)
                if pid in seen:
                    continue
                seen.add(pid)

                name_el = (
                    a.select_one("div.name")
                    or a.select_one("span.name")
                    or a.select_one("div.prod-name")
                )
                name = name_el.get_text(strip=True) if name_el else a.get_text(strip=True)[:60]
                if not href.startswith("http"):
                    href = "https://www.coupang.com" + href

                products.append({"product_id": pid, "product_name": name, "product_url": href})
                added += 1

            print(f"  페이지 {page_num}: 링크 {len(links)}개 (신규 {added}개) → 누계 {len(products)}개")

            if len(links) == 0:
                print("  더 이상 상품 없음, 종료")
                break

            page_num += 1
            time.sleep(random.uniform(1.5, 2.5))

        return products[:max_products]

    # ── 리뷰 수집 ─────────────────────────────────────────────────────
    def get_reviews(self, product_id, product_name, max_reviews=200, min_negative=20):
        import json as _json

        reviews      = []
        intercepted  = []   # 가로챈 리뷰 API 응답 저장

        def _on_response(response):
            if "next-api/review" in response.url and "batch" not in response.url and response.status == 200:
                try:
                    intercepted.append(response.json())
                except Exception:
                    pass

        self._page.on("response", _on_response)

        try:
            product_url = f"https://www.coupang.com/vp/products/{product_id}"
            self._goto(product_url, wait_ms=3000)

            # 상품평 탭 클릭 — 텍스트로 찾기
            tab_clicked = False
            try:
                # JS로 "상품평" 텍스트 포함된 <a> 태그 찾아서 클릭
                self._page.evaluate("""
                    () => {
                        const el = Array.from(document.querySelectorAll('a'))
                            .find(a => a.textContent.includes('상품평'));
                        if (el) { el.scrollIntoView(); el.click(); }
                    }
                """)
                tab_clicked = True
            except Exception:
                pass

            if not tab_clicked:
                for _ in range(8):
                    self._page.mouse.wheel(0, 600)
                    time.sleep(0.4)

            time.sleep(2)

            # 첫 번째 응답 대기 (최대 8초)
            for _ in range(16):
                if intercepted:
                    break
                time.sleep(0.5)

            if not intercepted:
                return reviews

            # 첫 페이지 처리
            def _parse(data):
                if not data or not isinstance(data, dict):
                    return []
                return data.get("rData", {}).get("paging", {}).get("contents", [])

            page_num = 1
            while len(reviews) < max_reviews:
                if page_num == 1:
                    # 이미 가로챈 첫 페이지 사용
                    data = intercepted[0]
                else:
                    # 다음 페이지: 브라우저 컨텍스트로 직접 API 요청 (페이지 이동 없음)
                    next_url = REVIEW_URL.format(pid=product_id, page=page_num)
                    referer = f"https://www.coupang.com/vp/products/{product_id}"
                    try:
                        resp = self._page.request.get(
                            next_url,
                            headers={"Referer": referer},
                            timeout=10000,
                        )
                        if resp.status != 200:
                            break
                        data = resp.json()
                    except Exception:
                        break
                    time.sleep(random.uniform(0.8, 1.5))

                item_list = _parse(data)
                if not item_list:
                    break

                for item in item_list:
                    if len(reviews) >= max_reviews:
                        break
                    content = item.get("content") or ""
                    if not content:
                        continue
                    review_at = item.get("reviewAt")
                    if review_at:
                        review_date = datetime.fromtimestamp(review_at / 1000).strftime("%Y-%m-%d")
                    else:
                        review_date = ""
                    reviews.append({
                        "review_id"     : str(item.get("reviewId", "")),
                        "product_name"  : product_name,
                        "product_id"    : product_id,
                        "rating"        : str(item.get("rating", "")),
                        "review_title"  : item.get("title", ""),
                        "review_content": content,
                        "review_date"   : review_date,
                        "nickname"      : item.get("displayName") or item.get("member", {}).get("name", ""),
                        "crawled_at"    : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    })

                paging = data.get("rData", {}).get("paging", {})
                total_pages = paging.get("totalPage", 1)
                if page_num >= total_pages:
                    break
                page_num += 1

            # 낮은 별점(1~2점) 최소 수집 보장
            neg_count = sum(1 for r in reviews if r["rating"] in ("1", "2"))
            if neg_count < min_negative:
                seen_ids = {r["review_id"] for r in reviews if r["review_id"]}
                referer = f"https://www.coupang.com/vp/products/{product_id}"
                for star in [1, 2]:
                    if neg_count >= min_negative:
                        break
                    pg = 1
                    while neg_count < min_negative:
                        url = REVIEW_URL_RATING.format(pid=product_id, page=pg, rating=star)
                        try:
                            resp = self._page.request.get(
                                url, headers={"Referer": referer}, timeout=10000
                            )
                            if resp.status != 200:
                                break
                            data = resp.json()
                        except Exception:
                            break
                        item_list = _parse(data)
                        if not item_list:
                            break
                        added = 0
                        for item in item_list:
                            rid = str(item.get("reviewId", ""))
                            if rid in seen_ids:
                                continue
                            content = item.get("content") or ""
                            if not content:
                                continue
                            seen_ids.add(rid)
                            review_at = item.get("reviewAt")
                            review_date = (
                                datetime.fromtimestamp(review_at / 1000).strftime("%Y-%m-%d")
                                if review_at else ""
                            )
                            reviews.append({
                                "review_id"     : rid,
                                "product_name"  : product_name,
                                "product_id"    : product_id,
                                "rating"        : str(item.get("rating", "")),
                                "review_title"  : item.get("title", ""),
                                "review_content": content,
                                "review_date"   : review_date,
                                "nickname"      : item.get("displayName") or item.get("member", {}).get("name", ""),
                                "crawled_at"    : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            })
                            neg_count += 1
                            added += 1
                        paging = data.get("rData", {}).get("paging", {})
                        if pg >= paging.get("totalPage", 1) or added == 0:
                            break
                        pg += 1
                        time.sleep(random.uniform(0.5, 1.0))

        finally:
            self._page.remove_listener("response", _on_response)

        return reviews

    # ── 단일 키워드 실행 ───────────────────────────────────────────────
    def run(self, keyword, max_products=50, max_reviews=200, min_negative=20):
        products = self.get_product_list(keyword, max_products)
        if not products:
            print("수집된 상품이 없습니다.")
            return pd.DataFrame()

        all_reviews = []
        print(f"\n[리뷰 수집] 상품 {len(products)}개 처리 시작")
        for i, prod in enumerate(tqdm(products, desc="상품별 리뷰 수집")):
            try:
                reviews = self.get_reviews(prod["product_id"], prod["product_name"], max_reviews, min_negative)
                all_reviews.extend(reviews)
            except Exception as e:
                print(f"  ⚠ 상품 {prod['product_id']} 실패, 스킵: {e}")

            # 상품 사이 딜레이
            time.sleep(random.uniform(2.0, 4.0))

            # 5개마다 홈 방문 후 긴 휴식 (사람처럼)
            if (i + 1) % 5 == 0:
                print(f"  [휴식] {i+1}개 완료, 잠시 대기 중...")
                self._goto("https://www.coupang.com", wait_ms=3000)
                self._random_scroll()
                time.sleep(random.uniform(15.0, 30.0))

        df = pd.DataFrame(all_reviews)
        print(f"\n총 {len(df):,}건 리뷰 수집 완료")
        return df

    # ── 다중 키워드 실행 ───────────────────────────────────────────────
    def run_multi_keyword(self, keywords, max_products=50, max_reviews=200, min_negative=20):
        all_dfs = []
        for i, kw in enumerate(keywords):
            print(f"\n{'='*50}\n키워드: {kw}\n{'='*50}")
            df = self.run(kw, max_products, max_reviews, min_negative)
            if not df.empty:
                df["keyword"] = kw
                all_dfs.append(df)
                # 키워드 완료마다 중간 저장
                mid_df = pd.concat(all_dfs, ignore_index=True)
                mid_file = f"coupang_reviews_partial_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                mid_df.to_csv(mid_file, index=False, encoding="utf-8-sig")
                print(f"  [중간 저장] {mid_file} ({len(mid_df):,}건)")
            # 키워드 사이 충분한 휴식
            if i < len(keywords) - 1:
                wait = random.uniform(60.0, 120.0)
                print(f"  [키워드 전환 대기] {wait:.0f}초 휴식 중...")
                time.sleep(wait)
        return pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()

    # ── 저장 ──────────────────────────────────────────────────────────
    def save(self, df, filename=None):
        if df.empty:
            print("저장할 데이터가 없습니다.")
            return None
        if filename is None:
            filename = f"coupang_reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"저장 완료: {filename}  ({len(df):,}건)")
        return filename

    # ── 요약 ──────────────────────────────────────────────────────────
    def summary(self, df):
        if df.empty:
            print("데이터가 없습니다.")
            return
        print("\n" + "="*50)
        print("수집 결과 요약")
        print("="*50)
        print(f"총 리뷰 수     : {len(df):,}건")
        print(f"수집 상품 수   : {df['product_id'].nunique():,}개")
        if "keyword" in df.columns:
            print("\n키워드별 리뷰 수:")
            print(df.groupby("keyword").size().to_string())
        try:
            avg = pd.to_numeric(df["rating"], errors="coerce").mean()
            print(f"\n평균 평점      : {avg:.2f}")
        except Exception:
            pass
        print("="*50)
