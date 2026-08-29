from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

print("=" * 55)
print("🕷️ [3단계] Playwright 로봇 브라우저로 네이버 뉴스 긁어오기")
print("=" * 55)

url = "https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=101"

print(f"🌐 1. 브라우저를 띄워 네이버 경제 뉴스에 접속 중: {url}")

with sync_playwright() as p:
    # 1. 브라우저 실행 (headless=True: 화면 없이 백그라운드에서 실행)
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(2000)  # 동적 콘텐츠 로딩을 위해 2초 대기

    # 2. 웹페이지의 전체 HTML 글자 가져오기
    html = page.content()
    browser.close()

print("✅ 2. 웹페이지 HTML 수집 완료!\n")

# 3. HTML 안에서 뉴스 제목과 링크만 쏙 골라내기 (BeautifulSoup)
soup = BeautifulSoup(html, "lxml")
articles = soup.select(".sh_headline_list > li, .sa_text")

print("-" * 55)
print(f"📰 [네이버 경제 실시간 뉴스 상위 3개 추출 (총 {len(articles)}개 발견)]")
print("-" * 55)

for idx, item in enumerate(articles[:3], 1):
    # 제목 찾기
    title_elem = item.select_one(".sh_headline_title, .sa_text_title")
    title = title_elem.get_text(strip=True) if title_elem else "제목 없음"
    
    # 링크 찾기
    link_elem = item.select_one("a")
    link = link_elem["href"] if link_elem and link_elem.has_attr("href") else "링크 없음"
    
    print(f"[{idx}] {title}")
    print(f"    - 링크: {link}")
    print()

print("🎉 [3단계 성공] API가 없는 사이트도 Playwright로 직접 긁어왔습니다!")