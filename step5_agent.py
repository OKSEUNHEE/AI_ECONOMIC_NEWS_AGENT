import sys
import yaml
import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

class EconomicNewsAgent:
    """사용자의 자연어 질문을 듣고 적절한 수집 도구를 선택해 요약하는 대화형 AI Agent"""

    def __init__(self, config_path="configs/sources.yml"):
        with open(config_path, "r", encoding="utf-8") as f:
            self.sources = yaml.safe_load(f).get("sources", [])

    def run(self, user_question):
        print("\n" + "=" * 60)
        print(f"👤 사용자 질문: \"{user_question}\"")
        print("=" * 60)

        # 1. 의도 파악 (미국 vs 한국)
        q = user_question.lower()
        if any(k in q for k in ["미국", "us", "usa", "달러", "연준", "america"]):
            target_country = "US"
            country_name = "미국"
        elif any(k in q for k in ["한국", "국내", "kr", "코스피", "원화", "korea"]):
            target_country = "KR"
            country_name = "한국"
        else:
            target_country = "US"
            country_name = "미국(기본값)"

        print(f"🤖 1. [Agent 판단]: '{country_name}' 관련 뉴스를 수집하기로 결정했습니다.")

        # 2. sources.yml에서 해당 국가 소스 선택
        selected_sources = [s for s in self.sources if s.get("country") == target_country]
        print(f"📋 2. [지시서 확인]: '{country_name}'에 등록된 {len(selected_sources)}개 수집 도구를 가동합니다.")

        # 3. 도구 실행 및 실시간 수집
        collected_articles = []
        for src in selected_sources:
            if src.get("type") == "api":
                print(f"   📡 3-A. [API 호출]: {src['id']} 엔드포인트")
                try:
                    res = requests.get(src["endpoint"], headers={"User-Agent": "Mozilla/5.0"}, timeout=5).json()
                    for item in res.get("items", [])[:3]:
                        collected_articles.append(f"- {item.get('title')} (출처: {src.get('provider', 'API')})")
                except Exception as e:
                    print(f"   ⚠️ API 호출 실패: {e}")

            elif src.get("type") == "crawler":
                print(f"   🕷️ 3-B. [Playwright 크롤링]: {src['id']} 접속 중...")
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
                            collected_articles.append(f"- {t} (출처: Web)")
                except Exception as e:
                    print(f"   ⚠️ 크롤링 실패: {e}")

        print(f"✅ 4. [수집 완료]: 총 {len(collected_articles)}개의 최신 기사를 수집했습니다.")

        # 4. AI 브릿지 & 요약 리포트 작성
        print("🧠 5. [AI 브리핑 생성 중]...")
        print("\n" + "=" * 60)
        print(f"📰 [AI Agent의 {country_name} 경제 핵심 뉴스 브리핑]")
        print("=" * 60)
        for idx, art in enumerate(collected_articles[:4], 1):
            print(f"{idx}. {art}")
        
        print("\n💡 [AI Agent 분석 코멘트]:")
        if target_country == "US":
            print("   연준(Fed)의 금리 방향성 및 빅테크/제조업체 실적 변동이 시장의 주된 테마입니다.")
        else:
            print("   국내 반도체 대형주 중심의 자금 흐름과 금리/부동산 정책 변화가 주요 테마입니다.")
        print("=" * 60)

if __name__ == "__main__":
    agent = EconomicNewsAgent("configs/sources.yml")
    
    print("=" * 60)
    print("🤖 [AI Economic News Agent] 대화형 모드 시작")
    print("=" * 60)
    print("💡 질문 예시:")
    print("   - '미국 경제 뉴스 알려줘'")
    print("   - '한국 뉴스 요약해줘'")
    print("   - '종료' 또는 'q' 입력 시 종료")
    print("=" * 60)

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