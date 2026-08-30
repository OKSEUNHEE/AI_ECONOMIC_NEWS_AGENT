import yfinance as yf
from typing import Dict, Any, List

class YFinanceTool:
    """특정 기업의 실시간 주가와 최신 뉴스를 수집하는 전용 도구"""

    # 대표적인 기업명 한글/영문 매핑 사전
    TICKER_MAP = {
        "테슬라": "TSLA", "tesla": "TSLA", "tsla": "TSLA",
        "애플": "AAPL", "apple": "AAPL", "aapl": "AAPL",
        "엔비디아": "NVDA", "nvidia": "NVDA", "nvda": "NVDA",
        "마이크로소프트": "MSFT", "microsoft": "MSFT", "msft": "MSFT",
        "구글": "GOOGL", "google": "GOOGL", "googl": "GOOGL", "알파벳": "GOOGL",
        "아마존": "AMZN", "amazon": "AMZN", "amzn": "AMZN",
        "삼성전자": "005930.KS", "삼성": "005930.KS",
        "sk하이닉스": "000660.KS", "하이닉스": "000660.KS",
        "현대차": "005380.KS", "현대자동차": "005380.KS"
    }

    @staticmethod
    def get_ticker_symbol(query: str) -> str:
        q = query.lower().strip()
        for name, symbol in YFinanceTool.TICKER_MAP.items():
            if name in q:
                return symbol
        # 티커 심볼 직접 입력 대응 (3~5자리 영문 대문자 등)
        return query.upper()

    @staticmethod
    def fetch_company(query: str) -> Dict[str, Any]:
        symbol = YFinanceTool.get_ticker_symbol(query)
        print(f"📈 [yfinance Tool] '{query}' ➔ 티커 '{symbol}' 조회 시작")

        try:
            company = yf.Ticker(symbol)
            info = company.info
            company_name = info.get("shortName", symbol)
            current_price = info.get("currentPrice") or info.get("regularMarketPrice") or "N/A"
            currency = info.get("currency", "USD")
            market_cap = info.get("marketCap", 0)

            # 뉴스 수집
            news_items = []
            for item in company.news[:4]:
                title = item.get("title") or (item.get("content", {}).get("title") if isinstance(item.get("content"), dict) else "제목 없음")
                link = item.get("link") or (item.get("content", {}).get("canonicalUrl", {}).get("url") if isinstance(item.get("content"), dict) else "")
                publisher = item.get("publisher") or (item.get("content", {}).get("provider", {}).get("displayName") if isinstance(item.get("content"), dict) else "Yahoo")
                if title:
                    news_items.append({
                        "title": title,
                        "link": link,
                        "publisher": publisher
                    })

            return {
                "success": True,
                "symbol": symbol,
                "name": company_name,
                "price": current_price,
                "currency": currency,
                "market_cap": market_cap,
                "news": news_items
            }

        except Exception as e:
            print(f"❌ [yfinance Tool] 조회 실패: {e}")
            return {"success": False, "error": str(e)}