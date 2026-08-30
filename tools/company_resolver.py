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
                cls._krx_stocks = fdr.StockListing('KRX')[['Code', 'Name', 'Market']]
            except Exception as e:
                cls._krx_stocks = None

    @classmethod
    def format_market_cap(cls, cap, currency):
        if not cap or cap == 0:
            return "정보 없음"
        if currency == "KRW":
            # 조 / 억 원 단위 변환
            jo = cap // 1000000000000
            eok = (cap % 1000000000000) // 100000000
            if jo > 0:
                return f"{jo}조 {eok:,}억 원"
            return f"{eok:,}억 원"
        else:
            # 달러 단위 (억 달러 / 조 달러)
            billion = cap / 1000000000
            if billion >= 1000:
                trillion = billion / 1000
                return f"약 {trillion:.2f}조 달러 (약 {billion:,.0f}억 달러)"
            return f"약 {billion:,.1f}억 달러"

    @classmethod
    def resolve_symbol(cls, query: str):
        q = query.lower().strip()
        
        # 1. 미국 대표 기업 사전 (스페이스X 공식 SPCX 포함)
        us_map = {
            "스페이스x": "SPCX", "스페이스엑스": "SPCX", "spacex": "SPCX", "spcx": "SPCX",
            "테슬라": "TSLA", "tesla": "TSLA", "tsla": "TSLA",
            "애플": "AAPL", "apple": "AAPL", "aapl": "AAPL",
            "엔비디아": "NVDA", "nvidia": "NVDA", "nvda": "NVDA",
            "마이크로소프트": "MSFT", "microsoft": "MSFT", "msft": "MSFT",
            "구글": "GOOGL", "google": "GOOGL", "googl": "GOOGL", "알파벳": "GOOGL",
            "아마존": "AMZN", "amazon": "AMZN", "amzn": "AMZN",
            "메타": "META", "meta": "META", "페이스북": "META",
            "넷플릭스": "NFLX", "netflix": "NFLX", "nflx": "NFLX",
            "amd": "AMD", "인텔": "INTC", "팔란티어": "PLTR",
            "로켓랩": "RKLB", "버진갤럭틱": "SPCE",
            "코카콜라": "KO", "스타벅스": "SBUX", "나이키": "NKE"
        }
        for name, sym in us_map.items():
            if name in q:
                return sym, name, "US"

        # 2. 영문 티커 직접 입력 (예: TSLA, AAPL, NVDA, SPCX 등)
        words = q.upper().split()
        for w in words:
            if len(w) <= 6 and w.isalpha() and w in us_map.values():
                return w, w, "US"

        # 3. 한국거래소(KRX) 전체 2,500개 상장사 자동 검색
        cls.load_krx()
        if cls._krx_stocks is not None:
            match = cls._krx_stocks[cls._krx_stocks['Name'].str.lower() == q]
            if match.empty:
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

        print(f"📈 [상장 기업 실시간 조회] '{query}' ➔ 티커 '{symbol}'")
        try:
            company = yf.Ticker(symbol)
            info = company.info or {}
            
            price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose") or "조회중"
            currency = "KRW" if market == "KR" else "USD"
            raw_cap = info.get("marketCap", 0)
            formatted_cap = cls.format_market_cap(raw_cap, currency)

            company_name = info.get("shortName") or name

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
                "name": company_name,
                "price": price,
                "currency": currency,
                "market_cap_str": formatted_cap,
                "news": news_list,
                "market": market
            }
        except Exception as e:
            return {"success": False, "reason": str(e)}