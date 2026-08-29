from bs4 import BeautifulSoup
from typing import Dict, Any, List
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright

class WebCrawler:
    """API가 없는 웹사이트를 Playwright로 렌더링하여 기사를 수집하는 도구"""

    @staticmethod
    def crawl(source_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        url = source_config.get("target_url")
        wait_time = source_config.get("wait_time", 2)
        selectors = source_config.get("selectors", {})
        container_sel = selectors.get("container")
        title_sel = selectors.get("title")
        link_sel = selectors.get("link", "a::attr(href)")
        press_sel = selectors.get("press")

        if not url or not container_sel:
            print(f"⚠️ [{source_config.get('id')}] URL 또는 container selector가 누락되었습니다.")
            return []

        print(f"🕷️ [Playwright Crawler] 브라우저 실행 및 접속: {url}")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                page.goto(url, wait_until="domcontentloaded")
                if wait_time > 0:
                    page.wait_for_timeout(wait_time * 1000)

                html_content = page.content()
                browser.close()

            # HTML 파싱
            soup = BeautifulSoup(html_content, "lxml")
            items = soup.select(container_sel)
            articles = []

            for item in items:
                # 제목 추출
                title_elem = item.select_one(title_sel) if title_sel else item
                title = title_elem.get_text(strip=True) if title_elem else ""

                # 링크 추출
                link = ""
                if "::attr(" in link_sel:
                    css_sel, attr_part = link_sel.split("::attr(")
                    attr_name = attr_part.rstrip(")")
                    target = item.select_one(css_sel.strip()) if css_sel.strip() else item
                    if target and target.has_attr(attr_name):
                        link = urljoin(url, target[attr_name].strip())
                else:
                    target = item.select_one(link_sel)
                    if target and target.has_attr("href"):
                        link = urljoin(url, target["href"].strip())

                # 언론사 추출
                press = ""
                if press_sel:
                    press_elem = item.select_one(press_sel)
                    press = press_elem.get_text(strip=True) if press_elem else ""

                if title and link:
                    articles.append({
                        "title": title,
                        "link": link,
                        "published_at": "",
                        "summary": "",
                        "source": press if press else source_config.get("id", "Web Crawler")
                    })

            print(f"✅ [Playwright Crawler] {len(articles)}건의 기사 크롤링 완료")
            return articles

        except Exception as e:
            print(f"❌ [Playwright Crawler] 크롤링 오류: {e}")
            return []

if __name__ == "__main__":
    test_cfg = {
        "id": "kr_economy_crawler",
        "target_url": "https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=101",
        "wait_time": 2,
        "selectors": {
            "container": ".sh_headline_list > li, .sa_text",
            "title": ".sh_headline_title, .sa_text_title",
            "link": "a::attr(href)",
            "press": ".sh_headline_press, .sa_text_press"
        }
    }
    res = WebCrawler.crawl(test_cfg)
    print(f"크롤러 테스트 결과: {len(res)}건 수집됨")
    if res:
        print("첫번째 기사 샘플:", res[0])