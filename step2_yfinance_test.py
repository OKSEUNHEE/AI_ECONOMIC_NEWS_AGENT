import yfinance as yf
import json

print("=" * 60)
print("📈 [yfinance 실습] 특정 기업 실시간 주가 및 최신 뉴스 수집")
print("=" * 60)

# 테스트할 기업 목록 (테슬라, 애플)
tickers = ["TSLA", "AAPL"]

for ticker_symbol in tickers:
    print(f"\n🔍 [{ticker_symbol}] 기업 데이터 조회 중...")
    company = yf.Ticker(ticker_symbol)
    
    # 1. 기업 기본 정보 및 주가
    info = company.info
    company_name = info.get("shortName", ticker_symbol)
    current_price = info.get("currentPrice") or info.get("regularMarketPrice")
    currency = info.get("currency", "USD")
    market_cap = info.get("marketCap", 0)

    print(f"🏢 기업명: {company_name}")
    print(f"💰 현재 주가: {current_price} {currency}")
    print(f"📊 시가총액: 약 {market_cap // 1000000000:,}B 달러")

    # 2. 기업 최신 뉴스 3건
    news_list = company.news
    print(f"\n📰 [{company_name} 최신 뉴스 3건]:")
    
    for idx, item in enumerate(news_list[:3], 1):
        # yfinance 최신 버전의 뉴스 딕셔너리 구조 대응
        title = item.get("title") or (item.get("content", {}).get("title") if isinstance(item.get("content"), dict) else "제목 없음")
        link = item.get("link") or (item.get("content", {}).get("canonicalUrl", {}).get("url") if isinstance(item.get("content"), dict) else "링크 없음")
        publisher = item.get("publisher") or (item.get("content", {}).get("provider", {}).get("displayName") if isinstance(item.get("content"), dict) else "Yahoo")

        print(f"   [{idx}] {title}")
        print(f"       • 언론사: {publisher}")
        print(f"       • 링크: {link}")

    print("-" * 60)

print("\n🎉 [yfinance 연동 성공] 주가(숫자)와 뉴스(글자)를 단 2줄로 모두 가져왔습니다!")