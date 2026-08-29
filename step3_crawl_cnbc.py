from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

print("=" * 55)
print("🕷️ [3단계] Playwright로 미국 CNBC 경제 뉴스 긁어오기")
print("=" * 55)

url = "https://www.cnbc.com/economy/"
print(f"🌐 1. 브라우저를 띄워 미국 CNBC에 접속 중: {url}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    html = page.content()
    browser.close()

print("✅ 2. CNBC 웹페이지 HTML 수집 완료!\n")

soup = BeautifulSoup(html, "lxml")
articles = soup.select(".Card-titleContainer, .RiverHeadline-headline, .Card-title")

print("-" * 55)
print(f"📰 [미국 CNBC 실시간 경제 뉴스 상위 3개 추출 (총 {len(articles)}개 발견)]")
print("-" * 55)

count = 0
for item in articles:
    title = item.get_text(strip=True)
    link_elem = item if item.name == 'a' else item.select_one('a')
    link = link_elem['href'] if link_elem and link_elem.has_attr('href') else ''

    if title and link and count < 3:
        count += 1
        print(f"[{count}] {title}")
        print(f"    - 링크: {link}")
        print()

print("🎉 [3단계 성공] 미국 CNBC 뉴스도 Playwright로 직접 긁어왔습니다!")