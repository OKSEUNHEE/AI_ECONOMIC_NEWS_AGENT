import os
import yfinance as yf
import FinanceDataReader as fdr
import pandas as pd

class CompanyResolver:
    """한국거래소(KRX 2,500개 주식 + 1,163개 ETF) 및 미국 전 종목/ETF 실시간 매핑 도구"""

    _krx_stocks = None

    @classmethod
    def load_krx(cls):
        if cls._krx_stocks is None:
            try:
                # 1. 주식 종목
                stocks = fdr.StockListing('KRX')[['Code', 'Name', 'Market']]
                # 2. 국내 ETF 종목
                etfs = fdr.StockListing('ETF/KR')[['Symbol', 'Name']]
                etfs = etfs.rename(columns={'Symbol': 'Code'})
                etfs['Market'] = 'ETF'
                
                cls._krx_stocks = pd.concat([stocks, etfs], ignore_index=True)
            except Exception as e:
                cls._krx_stocks = None

    @classmethod
    def format_market_cap(cls, cap, currency):
        if not cap or cap == 0:
            return "ETF/지수 펀드 (순자산 기준)"
        if currency == "KRW":
            jo = cap // 1000000000000
            eok = (cap % 1000000000000) // 100000000
            if jo > 0:
                return f"{jo}조 {eok:,}억 원"
            return f"{eok:,}억 원"
        else:
            billion = cap / 1000000000
            if billion >= 1000:
                trillion = billion / 1000
                return f"약 {trillion:.2f}조 달러 (약 {billion:,.0f}억 달러)"
            return f"약 {billion:,.1f}억 달러"

    @classmethod
    def resolve_symbol(cls, query: str):
        q = query.lower().strip()
        
        # 1. 미국 대표 주식 및 인기 ETF
        us_map = {
            "spy": "SPY", "qqq": "QQQ", "soxx": "SOXX", "smh": "SMH",
            "schd": "SCHD", "voo": "VOO", "ivv": "IVV", "tlt": "TLT",
            "tqqq": "TQQQ", "sqqq": "SQQQ", "dia": "DIA", "arkk": "ARKK",
            "스페이스x": "SPCX", "spacex": "SPCX", "spcx": "SPCX",
            "테슬라": "TSLA", "애플": "AAPL", "엔비디아": "NVDA",
            "마이크로소프트": "MSFT", "구글": "GOOGL", "아마존": "AMZN",
            "메타": "META", "넷플릭스": "NFLX", "amd": "AMD", "인텔": "INTC",
            "팔란티어": "PLTR", "코카콜라": "KO", "스타벅스": "SBUX"
        }
        for name, sym in us_map.items():
            if name == q:
                return sym, sym, "US"

        # 2. 영문 1~5자리 미국 티커
        clean_q = query.strip().upper()
        if clean_q.isalpha() and 1 <= len(clean_q) <= 5:
            return clean_q, clean_q, "US"

        # 3. 한국 전체 주식(2,500개) + 한국 전체 ETF(1,163개)
        cls.load_krx()
        if cls._krx_stocks is not None:
            q_nospace = q.replace(" ", "")
            # 완전 일치
            match = cls._krx_stocks[cls._krx_stocks['Name'].str.lower().str.replace(" ", "") == q_nospace]
            if match.empty:
                # 포함 일치
                match = cls._krx_stocks[cls._krx_stocks['Name'].apply(lambda x: q_nospace in x.lower().replace(" ", ""))]

            if not match.empty:
                row = match.iloc[0]
                code = row['Code']
                market = row['Market']
                suffix = ".KS" if market in ["KOSPI", "KOSPI200", "ETF"] else ".KQ"
                return f"{code}{suffix}", row['Name'], "KR"

        return None, None, None

    @classmethod
    def fetch_company_info(cls, query: str):
        symbol, name, market = cls.resolve_symbol(query)
        if not symbol:
            return {"success": False, "reason": "NOT_FOUND"}

        print(f"📈 [실시간 가격/뉴스 조회] '{query}' ➔ 티커 '{symbol}'")
        try:
            ticker = yf.Ticker(symbol)
            price = None
            try:
                price = ticker.fast_info.get("lastPrice") or ticker.fast_info.get("regularMarketPrice")
            except:
                pass

            if not price:
                try:
                    hist = ticker.history(period="1d")
                    if not hist.empty:
                        price = hist['Close'].iloc[-1]
                except:
                    pass

            info = ticker.info or {}
            if not price:
                price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("navPrice") or info.get("previousClose")

            currency = "KRW" if market == "KR" else "USD"
            if isinstance(price, (int, float)):
                price_str = f"{price:,.0f} 원" if currency == "KRW" else f"${price:,.2f}"
            else:
                price_str = str(price) if price else "조회중"

            raw_cap = info.get("marketCap") or ticker.fast_info.get("marketCap", 0)
            formatted_cap = cls.format_market_cap(raw_cap, currency)
            company_name = info.get("shortName") or info.get("longName") or name

            news_list = []
            for item in (ticker.news or [])[:4]:
                title = item.get("title") or (item.get("content", {}).get("title") if isinstance(item.get("content"), dict) else "")
                link = item.get("link") or (item.get("content", {}).get("canonicalUrl", {}).get("url") if isinstance(item.get("content"), dict) else "")
                pub = item.get("publisher") or (item.get("content", {}).get("provider", {}).get("displayName") if isinstance(item.get("content"), dict) else "Yahoo")
                if title:
                    news_list.append({"title": title, "link": link, "publisher": pub})

            return {
                "success": True,
                "symbol": symbol,
                "name": company_name,
                "price": price_str,
                "currency": currency,
                "market_cap_str": formatted_cap,
                "news": news_list,
                "market": market
            }
        except Exception as e:
            return {"success": False, "reason": str(e)}