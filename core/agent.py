import os
import yaml
from typing import Dict, Any, List
from tools.api_fetcher import ApiFetcher
from tools.web_crawler import WebCrawler
from core.normalizer import NewsNormalizer

class EconomicNewsAgent:
    """사용자의 자연어 질문을 이해하고 뉴스 수집 및 분석을 수행하는 AI Agent"""

    def __init__(self, config_path: str = "configs/sources.yml"):
        self.config_path = config_path
        self.sources = self._load_sources()

    def _load_sources(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"지시서 파일을 찾을 수 없습니다: {self.config_path}")
        with open(self.config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data.get("sources", [])

    def process_query(self, user_query: str) -> Dict[str, Any]:
        """사용자 질문을 분석하고 적합한 수집 도구를 호출하여 최종 브리핑 리포트를 생성합니다."""
        print(f"\n🤖 [AI Agent] 사용자 질문 분석 중: \"{user_query}\"")

        # 1. 의도 및 국가 파악
        q_lower = user_query.lower()
        if any(k in q_lower for k in ["미국", "us", "usa", "미증시", "달러", "연준"]):
            target_country = "US"
            country_name = "미국"
        elif any(k in q_lower for k in ["한국", "국내", "kr", "코스피", "원화"]):
            target_country = "KR"
            country_name = "한국"
        else:
            target_country = "ALL"
            country_name = "글로벌/종합"

        print(f"🎯 [AI Agent] 타겟 국가 감지: {country_name} ({target_country})")

        # 2. 적합한 수집 소스 필터링
        selected_sources = []
        for src in self.sources:
            if target_country == "ALL" or src.get("country") == target_country:
                selected_sources.append(src)

        if not selected_sources:
            return {"error": f"'{country_name}'에 해당하는 등록된 수집 소스가 없습니다."}

        print(f"📋 [AI Agent] 총 {len(selected_sources)}개의 수집 경로(API / Web Crawler)를 가동합니다.")

        # 3. 도구 실행 및 수집 (Tool Execution)
        all_raw_articles = []
        for src in selected_sources:
            src_type = src.get("type")
            src_id = src.get("id")

            if src_type == "api":
                print(f"  └─ 📡 [API 호출] {src_id}")
                articles = ApiFetcher.fetch_news(src)
                all_raw_articles.extend(articles)
            elif src_type == "crawler":
                print(f"  └─ 🕷️ [Playwright 크롤링] {src_id}")
                articles = WebCrawler.crawl(src)
                all_raw_articles.extend(articles)

        # 4. 데이터 정제 및 표준화 (Normalization)
        normalized_articles = NewsNormalizer.normalize(all_raw_articles, target_country, "economy")
        saved_json = NewsNormalizer.save_to_json(normalized_articles, f"{target_country.lower()}_news")
        print(f"💾 [AI Agent] 총 {len(normalized_articles)}건의 유효 기사를 정제하여 저장했습니다: {saved_json}")

        # 5. AI 지능형 분석 및 요약 브리핑 생성
        briefing = self._generate_briefing(country_name, normalized_articles)

        return {
            "query": user_query,
            "country": country_name,
            "total_articles": len(normalized_articles),
            "saved_file": saved_json,
            "briefing": briefing,
            "articles": normalized_articles[:10]
        }

    def _generate_briefing(self, country_name: str, articles: List[Dict[str, Any]]) -> str:
        """수집된 기사 데이터를 바탕으로 핵심 경제 브리핑 리포트를 작성합니다."""
        if not articles:
            return f"현재 {country_name} 관련 최신 뉴스를 찾을 수 없습니다."

        # 기사 분류 키워드 매칭
        topics = {
            "금리 / 통화 / 물가": [],
            "증시 / 기업 / 실적": [],
            "산업 / 기술 / 무역": [],
            "기타 경제 이슈": []
        }

        for art in articles:
            t = art["title"].lower()
            if any(k in t for k in ["금리", "연준", "fed", "물가", "인플레", "환율", "cpi", "rate", "inflation", "dollar"]):
                topics["금리 / 통화 / 물가"].append(art)
            elif any(k in t for k in ["증시", "주가", "실적", "주식", "코스피", "나스닥", "stock", "market", "earnings", "company"]):
                topics["증시 / 기업 / 실적"].append(art)
            elif any(k in t for k in ["반도체", "ai", "수출", "무역", "배터리", "chip", "trade", "tech", "export"]):
                topics["산업 / 기술 / 무역"].append(art)
            else:
                topics["기타 경제 이슈"].append(art)

        lines = []
        lines.append(f"📊 [오늘의 {country_name} 경제 핵심 브리핑 (총 {len(articles)}개 기사 분석)]\n")

        for topic_name, topic_arts in topics.items():
            if topic_arts:
                lines.append(f"🔹 **{topic_name}** ({len(topic_arts)}건)")
                for art in topic_arts[:3]: # 카테고리당 최대 3개
                    lines.append(f"   • {art['title']} [{art['source']}]")
                lines.append("")

        lines.append("💡 **AI Agent 종합 코멘트:**")
        if country_name == "미국":
            lines.append("   글로벌 금리 방향성과 빅테크/고용 지표를 중심으로 시장 변동성이 주목받고 있습니다.")
        elif country_name == "한국":
            lines.append("   국내 수출 지표 및 반도체/금융 관련 정책 및 기업 이슈가 주요 관심사로 파악됩니다.")
        else:
            lines.append("   글로벌 주요 경제권의 통화 정책과 거시 경제 지표 발표에 유의할 필요가 있습니다.")

        return "\n".join(lines)