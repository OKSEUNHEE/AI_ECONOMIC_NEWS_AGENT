import os
import json
import time
from typing import List, Dict, Any

class NewsNormalizer:
    """수집된 뉴스 데이터를 표준 JSON 스키마로 정제하고 중복을 제거하는 클래스"""

    @staticmethod
    def normalize(raw_articles: List[Dict[str, Any]], country: str, topic: str) -> List[Dict[str, Any]]:
        normalized = []
        seen_links = set()
        seen_titles = set()

        for art in raw_articles:
            title = art.get("title", "").strip()
            link = art.get("link", "").strip()
            source = art.get("source", "Unknown").strip()
            published_at = art.get("published_at", "").strip()
            summary = art.get("summary", "").strip()

            if not title or not link:
                continue

            # 중복 체크 (URL 및 제목 기준)
            if link in seen_links or title in seen_titles:
                continue
            seen_links.add(link)
            seen_titles.add(title)

            normalized.append({
                "country": country.upper(),
                "topic": topic.lower(),
                "title": title,
                "link": link,
                "source": source if source else "경제뉴스",
                "published_at": published_at if published_at else "최신",
                "summary": summary
            })

        return normalized

    @staticmethod
    def save_to_json(data: List[Dict[str, Any]], filename_prefix: str = "news") -> str:
        os.makedirs("data", exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join("data", f"{filename_prefix}_{timestamp}.json")

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({
                "collected_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_count": len(data),
                "articles": data
            }, f, ensure_ascii=False, indent=2)

        return filepath