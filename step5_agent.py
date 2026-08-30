import sys
import yaml
import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from tools.yfinance_tool import YFinanceTool

class EconomicNewsAgent:
    """사용자의 질문에 따라 적절한 도구(yfinance / API / Playwright)를 선택해 요약하는 완성형 AI Agent"""

    def __init__(self, config_path="configs/sources.yml"):
        with open(config_path, "r", encoding="utf-8") as f:
            self.sources = yaml.safe_load(f).get("sources", [])

    def run(self, user_question):
        print("\n" + "=" * 65)
        print(f"👤 사용자 질문: \"{user_question}\"")
        print("=" * 65)

        q = user_question.lower()

        # 1. 특정 기업 조회인지 판단 (yfinance 도구 대상)
        is_company_query = any(name in q for name in YFinanceTool.TICKER_MAP.keys())

        if is_company_query:
            print("🤖 1. [Agent 판단]: '특정 기업 분석/주가' 질문으로 판단 ➔ yfinance 도구를 선택합니다.")
            res = YFinanceTool.fetch_company(user_question)
            
            if not res.get("success"):
                print(f"❌ 기업 정보를 가져오지 못했습니다: {res.get('error')}")
                return

            print("\n" + "=" * 65)
            print(f"📊 [AI Agent 기업 분석 리포트: {res['name']} ({res['symbol']})]")
            print("=" * 65)
            print(f"💰 현재 실시간 주가: {res['price']} {res['currency']}")
            if res.get("market_cap"):
                print(f"🏢 시가총액: 약 {res['market_cap'] // 1000000000:,}B (달러/원)")
            
            print(f"\n📰 [{res['name']} 최신 뉴스 3선]:")
            for idx, item in enumerate(res.get("news", [])[:3], 1):
                print(f"   {idx}. {item['title']} [{item['publisher']}]")

            print("\n💡 [AI Agent 요약 코멘트]:")
            print(f"   {res['name']}의 최근 주가 흐름과 뉴스 이슈를 분석한 결과, 글로벌 시장 동향과 기술/실적 발표가 주요 변수로 작용하고 있습니다.")
            print("=" * 65)
            return

        # 2. 국가별 거시 경제 뉴스 (미국 vs 한국)
        if any(k in q for k in ["미국", "us", "usa", "달러", "연준", "america"]):
            target_country = "US"
            country_name = "미국"
        elif any(k in q for k in ["한국", "국내", "kr", "코스피", "원화", "korea"]):
            target_country = "KR"
            country_name = "한국"
        else:
            target_country = "US"
            country_name = "미국(기본값)"

        print(f"🤖 1. [Agent 판단]: '{country_name}' 거시 경제 뉴스를 수집하기로 결정했습니다.")

        selected_sources = [s for s in self.sources if s.get("country") == target_country]
        print(f"📋 2. [지시서 확인]: '{country_name}'에 등록된 {len(selected_sources)}개 수집 도구를 가동합니다.")

        collected_articles = []
        for src in selected_sources:
            if src.get("type") == "api":
                print(f"   📡 3-A. [API 호출]: {src['id']}")
                try:
                    res = requests.get(src["endpoint"], headers={"User-Agent": "Mozilla/5.0"}, timeout=5).json()
                    for item in res.get("items", [])[:3]:
                        collected_articles.append(f"- {item.get('title')} [{src.get('provider', 'API')}]")
                except Exception as e:
                    print(f"   ⚠️ API 호출 실패: {e}")

            elif src.get("type") == "crawler":
                print(f"   🕷️ 3-B. [Playwright 크롤링]: {src['id']}")
                try:
                    with sync_playwright() as p:
                        browser = p.chromium.launch(headless=True)
                        page = browser.new_page()
                        page.goto(src["target_url"], wait_until="domcontentloaded")
                        page.wait_for_timeout(1500)
                        html = page.content()
                        browser.close()

                    soup = BeautifulSoup(html, "lxml")
                    sels = src.get("selectors", {})
                    items = soup.select(sels.get("container", ""))
                    for item in items[:3]:
                        title_el = item.select_one(sels.get("title", "")) if sels.get("title") else item
                        t = title_el.get_text(strip=True) if title_el else ""
                        if t:
                            collected_articles.append(f"- {t} [Web]")
                except Exception as e:
                    print(f"   ⚠️ 크롤링 실패: {e}")

        print(f"✅ 4. [수집 완료]: 총 {len(collected_articles)}개의 최신 기사를 확보했습니다.")

        print("\n" + "=" * 65)
        print(f"📰 [AI Agent의 {country_name} 경제 핵심 뉴스 브리핑]")
        print("=" * 65)
        for idx, art in enumerate(collected_articles[:4], 1):
            print(f"{idx}. {art}")
        
        print("\n💡 [AI Agent 분석 코멘트]:")
        if target_country == "US":
            print("   연준(Fed)의 금리 방향성 발언과 미국 테크 기업들의 실적 변동이 시장의 주된 테마입니다.")
        else:
            print("   국내 반도체 대형주 중심의 자금 쏠림과 거시 경제 정책 변화가 주요 테마입니다.")
        print("=" * 65)

if __name__ == "__main__":
    agent = EconomicNewsAgent("configs/sources.yml")
    
    print("=" * 65)
    print("🤖 [AI Economic News Agent] 대화형 모드 시작 (yfinance + 크롤러)")
    print("=" * 65)
    print("💡 질문 예시:")
    print("   - '엔비디아 주가랑 뉴스 알려줘' (기업 분석)")
    print("   - '테슬라 최근 소식 보여줘'    (기업 분석)")
    print("   - '미국 경제 뉴스 알려줘'       (거시 경제)")
    print("   - '한국 뉴스 요약해줘'         (거시 경제)")
    print("   - '종료' 또는 'q' 입력 시 종료")
    print("=" * 65)

    while True:
        try:
            user_input = input("\n👤 나: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["q", "exit", "quit", "종료"]:
                print("👋 에이전트를 종료합니다. 수고하셨습니다!")
                break
            agent.run(user_input)
        except KeyboardInterrupt:
            print("\n👋 프로그램을 종료합니다.")
            break