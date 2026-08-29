import requests
from typing import Dict, Any, List

class ApiFetcher:
    """뉴스 API 엔드포인트를 호출하여 JSON 데이터를 수집하는 도구"""

    @staticmethod
    def fetch_news(source_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        endpoint = source_config.get("endpoint")
        if not endpoint:
            print(f"⚠️ [{source_config.get('id')}] API 엔드포인트가 정의되지 않았습니다.")
            return []

        print(f"📡 [API Fetcher] API 요청 전송: {endpoint}")
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
            }
            response = requests.get(endpoint, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            articles = []
            # rss2json 포맷 처리 (Yahoo Finance 등)
            if "items" in data:
                for item in data["items"]:
                    articles.append({
                        "title": item.get("title", "").strip(),
                        "link": item.get("link", "").strip(),
                        "published_at": item.get("pubDate", ""),
                        "summary": item.get("description", ""),
                        "source": item.get("author") or source_config.get("provider", "API")
                    })
            # 표준 NewsAPI 포맷 처리
            elif "articles" in data:
                for item in data["articles"]:
                    articles.append({
                        "title": item.get("title", "").strip(),
                        "link": item.get("url", "").strip(),
                        "published_at": item.get("publishedAt", ""),
                        "summary": item.get("description", ""),
                        "source": item.get("source", {}).get("name", "API")
                    })

            print(f"✅ [API Fetcher] {len(articles)}건의 기사 데이터 수집 완료")
            return articles

        except Exception as e:
            print(f"❌ [API Fetcher] API 호출 실패: {e}")
            return []

if __name__ == "__main__":
    test_cfg = {
        "id": "test_us",
        "provider": "Yahoo Finance RSS",
        "endpoint": "https://api.rss2json.com/v1/api.json?rss_url=https://finance.yahoo.com/news/rssindex"
    }
    res = ApiFetcher.fetch_news(test_cfg)
    print(f"테스트 결과: {len(res)}건 수집됨")
    if res:
        print("첫번째 기사 샘플:", res[0])