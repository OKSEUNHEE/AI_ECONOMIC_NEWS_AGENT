import sys
import yaml
import requests
from urllib.parse import quote
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from tools.company_resolver import CompanyResolver

class EconomicNewsAgent:
    def __init__(self, config_path="configs/sources.yml"):
        with open(config_path, "r", encoding="utf-8") as f:
            self.sources = yaml.safe_load(f).get("sources", [])

    def run(self, user_question):
        print("\n" + "=" * 65)
        print(f"👤 사용자 질문: \"{user_question}\"")
        print("=" * 65)

        q = user_question.lower()

        # 1. 거시 경제 질문인지 확인 (미국 vs 한국)
        if any(k in q for k in ["미국 경제", "미국 뉴스", "us economy", "미국 증시", "연준"]):
            target_country = "US"
            country_name = "미국"
            self._handle_macro(target_country, country_name)
            return
        elif any(k in q for k in ["한국 경제", "국내 경제", "한국 뉴스", "코스피 시황"]):
            target_country = "KR"
            country_name = "한국"
            self._handle_macro(target_country, country_name)
            return

        # 2. 상장 기업/주식 질문인지 한국거래소(KRX) 및 미국 주식(SPCX, TSLA 등) 자동 조회!
        res = CompanyResolver.fetch_company_info(user_question)
        if res.get("success"):
            print(f"🤖 1. [Agent 판단]: '{res['name']}' 상장 기업 실시간 분석으로 감지했습니다.")
            print("\n" + "=" * 65)
            print(f"📊 [AI Agent 기업 분석 리포트: {res['name']} ({res['symbol']})]")
            print("=" * 65)
            print(f"💰 실시간 현재 가격: {res['price']}")
            print(f"🏢 시가총액(몸값): {res.get('market_cap_str', '정보 없음')}")
            
            news_items = res.get("news", [])
            if not news_items:
                print(f"\n📰 [{res['name']} 실시간 뉴스 크롤러 가동 중...]")
                news_items = self._crawl_live_news(res['name'])
            
            print(f"\n📰 [{res['name']} 최신 주요 뉴스]:")
            for idx, item in enumerate(news_items[:3], 1):
                print(f"   {idx}. {item.get('title')} [{item.get('publisher', item.get('source', '뉴스'))}]")
            print("=" * 65)
            return

        # 3. 비상장사/일반 키워드 (예: 당근마켓, 토스, 비트코인 등)
        print(f"🤖 1. [Agent 판단]: '{user_question}' 맞춤 키워드 ➔ 실시간 뉴스 검색 크롤러를 가동합니다!")
        news_items = self._crawl_live_news(user_question)
        print(f"✅ 2. [수집 완료]: '{user_question}' 관련 최신 뉴스 {len(news_items)}건 수집 완료.\n")
        print("=" * 65)
        print(f"📰 [AI Agent '{user_question}' 실시간 뉴스 브리핑]")
        print("=" * 65)
        for idx, item in enumerate(news_items[:4], 1):
            print(f"{idx}. {item['title']} [{item['publisher']}]")
        print("=" * 65)

    def _crawl_live_news(self, keyword):
        search_url = f"https://search.daum.net/search?w=news&q={quote(keyword)}"
        results = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(search_url, wait_until="domcontentloaded")
                page.wait_for_timeout(1000)

                links = page.locator("div.item-title a, a[class*='tit_main'], strong.tit-g a").all()
                for l in links:
                    t = l.inner_text().strip()
                    h = l.get_attribute("href") or ""
                    if len(t) > 6 and h and not any(r["title"] == t for r in results):
                        results.append({
                            "title": t,
                            "publisher": "실시간 뉴스",
                            "link": h
                        })
                browser.close()
        except Exception as e:
            print(f"크롤링 중 오류: {e}")
        return results

    def _handle_macro(self, target_country, country_name):
        print(f"🤖 1. [Agent 판단]: '{country_name}' 거시 경제 뉴스를 수집합니다.")
        selected_sources = [s for s in self.sources if s.get("country") == target_country]
        collected = []
        for src in selected_sources:
            if src.get("type") == "api":
                try:
                    res = requests.get(src["endpoint"], headers={"User-Agent": "Mozilla/5.0"}, timeout=5).json()
                    for item in res.get("items", [])[:3]:
                        collected.append(f"- {item.get('title')} [{src.get('provider', 'API')}]")
                except: pass
            elif src.get("type") == "crawler":
                try:
                    with sync_playwright() as p:
                        browser = p.chromium.launch(headless=True)
                        page = browser.new_page()
                        page.goto(src["target_url"], wait_until="domcontentloaded")
                        page.wait_for_timeout(1500)
                        html = page.content()
                        browser.close()
                    soup = BeautifulSoup(html, "lxml")
                    for item in soup.select(src.get("selectors", {}).get("container", ""))[:3]:
                        t_el = item.select_one(src.get("selectors", {}).get("title", "")) if src.get("selectors", {}).get("title") else item
                        t = t_el.get_text(strip=True) if t_el else ""
                        if t: collected.append(f"- {t} [Web]")
                except: pass

        print("\n" + "=" * 65)
        print(f"📰 [AI Agent의 {country_name} 경제 핵심 뉴스 브리핑]")
        print("=" * 65)
        for idx, art in enumerate(collected[:4], 1):
            print(f"{idx}. {art}")
        print("=" * 65)

if __name__ == "__main__":
    agent = EconomicNewsAgent("configs/sources.yml")
    print("=" * 65)
    print("🤖 [AI Economic News Agent] 올인원 지능형 에이전트 시작")
    print("=" * 65)
    print("💡 어떤 질문이든 자유롭게 입력해보세요:")
    print("   - 상장 기업: '스페이스X', '테슬라', '카카오', '엔비디아', '삼성전자' 등")
    print("   - 비상장 기업/키워드: '당근마켓', '토스', '비트코인' 등")
    print("   - 거시 경제: '미국 경제 뉴스', '한국 경제 뉴스'")
    print("   - 'q' 또는 '종료' 입력 시 종료")
    print("=" * 65)

    while True:
        try:
            user_input = input("\n👤 나: ").strip()
            if not user_input: continue
            if user_input.lower() in ["q", "exit", "quit", "종료"]: break
            agent.run(user_input)
        except KeyboardInterrupt: break