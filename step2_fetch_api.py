import requests
import json

print("=" * 55)
print("📡 [2단계] 뉴스 API 호출 및 JSON 데이터 수집 시작")
print("=" * 55)

# 1. 1단계 YAML에서 정의했던 미국 뉴스 API 엔드포인트
api_url = "https://api.rss2json.com/v1/api.json?rss_url=https://finance.yahoo.com/news/rssindex"

print(f"🌐 1. API 주소로 요청 전송: {api_url}")
response = requests.get(api_url, headers={"User-Agent": "Mozilla/5.0"})

# 2. 응답받은 데이터를 파이썬 딕셔너리(JSON)로 변환
news_data = response.json()

print("✅ 2. JSON 데이터 수신 성공!\n")
print(f"📊 수신된 전체 기사 개수: {len(news_data.get('items', []))}개")
print("-" * 55)
print("📰 [최신 미국 경제 뉴스 상위 3개 확인]")
print("-" * 55)

# 3. 상위 3개 기사만 화면에 보기 좋게 출력
for idx, article in enumerate(news_data.get("items", [])[:3], 1):
    print(f"[{idx}] {article.get('title')}")
    print(f"    - 날짜: {article.get('pubDate')}")
    print(f"    - 링크: {article.get('link')}")
    print()

print("🎉 [2단계 성공] 브라우저 없이 API로 실시간 뉴스를 가져왔습니다!")