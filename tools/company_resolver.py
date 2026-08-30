import os
import yfinance as yf
import FinanceDataReader as fdr

class CompanyResolver:
    """한국거래소(KRX) 2,500개 전체 상장사 및 미국 주요 종목을 자동으로 매핑해주는 도구"""

    _krx_stocks = None

    @classmethod
    def load_krx(cls):
        if cls._krx_stocks is None:
            try:
                # KRX 전체 상장사 목록을 인터넷에서 자동 로드
                cls._krx_stocks = fdr.StockListing('KRX')[['Code', 'Name', 'Market']]
            except Exception as e:
                cls._krx_stocks = None

    @classmethod
    def resolve_symbol(cls, query: str):
        q = query.lower().strip()
        
        # 1. 미국 대표 기업 사전
        us_map = {
            "테슬라": "TSLA", "tesla": "TSLA", "애플": "AAPL", "apple": "AAPL",
            "엔비디아": "NVDA", "nvidia": "NVDA", "마이크로소프트": "MSFT", "msft": "MSFT",
            "구글": "GOOGL", "google": "GOOGL", "알파벳": "GOOGL",
            "아마존": "AMZN", "amazon": "AMZN", "메타": "META", "meta": "META",
            "넷플릭스": "NFLX", "netflix": "NFLX", "amd": "AMD", "인텔": "INTC",
            "팔란티어": "PLTR", "코카콜라": "KO", "스타벅스": "SBUX", "나이키": "NKE"
        }
        for name, sym in us_map.items():
            if name in q:
                return sym, name, "US"

        # 2. 영문 티커 직접 입력 (예: TSLA, AAPL, NVDA)
        words = q.upper().split()
        for w in words:
            if len(w) <= 6 and w.isalpha() and w in ["TSLA", "AAPL", "NVDA", "MSFT", "GOOGL", "AMZN", "META", "NFLX", "AMD", "INTC", "PLTR", "KO", "SBUX", "NKE"]:
                return w, w, "US"

        # 3. 한국거래소(KRX) 전체 2,500개 상장사 자동 검색!
        cls.load_krx()
        if cls._krx_stocks is not None:
            # 완전 일치 검색
            match = cls._krx_stocks[cls._krx_stocks['Name'].str.lower() == q]
            if match.empty:
                # 포함 검색
                match = cls._krx_stocks[cls._krx_stocks['Name'].apply(lambda x: x.lower() in q or q in x.lower())]

            if not match.empty:
                row = match.iloc[0]
                code = row['Code']
                market = row['Market']
                suffix = ".KS" if market == "KOSPI" else ".KQ"
                return f"{code}{suffix}", row['Name'], "KR"

        return None, None, None

    @classmethod
    def fetch_company_info(cls, query: str):
        symbol, name, market = cls.resolve_symbol(query)
        if not symbol:
            return {"success": False, "reason": "NOT_FOUND"}

        print(f"📈 [자동 기업 검색] '{query}' ➔ '{name}' ({symbol}) 자동 매핑 성공!")
        try:
            company = yf.Ticker(symbol)
            info = company.info or {}
            
            price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose") or "조회중"
            currency = "KRW" if market == "KR" else "USD"
            market_cap = info.get("marketCap", 0)

            news_list = []
            for item in (company.news or [])[:4]:
                title = item.get("title") or (item.get("content", {}).get("title") if isinstance(item.get("content"), dict) else "")
                link = item.get("link") or (item.get("content", {}).get("canonicalUrl", {}).get("url") if isinstance(item.get("content"), dict) else "")
                pub = item.get("publisher") or (item.get("content", {}).get("provider", {}).get("displayName") if isinstance(item.get("content"), dict) else "Yahoo")
                if title:
                    news_list.append({"title": title, "link": link, "publisher": pub})

            return {
                "success": True,
                "symbol": symbol,
                "name": name,
                "price": price,
                "currency": currency,
                "market_cap": market_cap,
                "news": news_list,
                "market": market
            }
        except Exception as e:
            return {"success": False, "reason": str(e)}