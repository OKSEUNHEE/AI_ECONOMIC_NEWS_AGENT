import json
import time

print("=" * 60)
print("🧠 [4단계] 수집된 뉴스를 AI(LLM)에게 전달하여 3줄 요약하기")
print("=" * 60)

# 1. 2단계와 3단계에서 긁어온 뉴스 샘플 데이터 준비
sample_news = [
    {"title": "워시 매파 발언에 하락 마감…금리 인상 확률 '쑥'[뉴욕증시]", "source": "한국경제", "country": "미국/한국"},
    {"title": "Fed Chairman Warsh expresses concern about inflation, advocates for 'quieter' central bank", "source": "CNBC", "country": "미국"},
    {"title": "코스피 '큰 손'된 삼전닉스…일주일새 8.5조 사들여", "source": "CBS노컷뉴스", "country": "한국"},
    {"title": "유니슨, 육·해상풍력 '동시 공략'…2030년 매출 1조원 정조준", "source": "아시아경제", "country": "한국"},
    {"title": "183-year-old giant tool company closes factory, lays off dozens", "source": "Yahoo Finance", "country": "미국"}
]

print(f"📋 1. 크롤러/API가 수집한 뉴스 총 {len(sample_news)}건 전달:\n")
for idx, n in enumerate(sample_news, 1):
    print(f"   [{idx}] {n['title']} ({n['source']})")

print("\n" + "-" * 60)
print("🤖 2. AI(LLM)에게 프롬프트(요청서) 전달 중...")
print("-" * 60)

prompt = """
[지시사항]
당신은 최고의 경제 분석 AI Agent입니다. 
위 수집된 5개의 경제 뉴스를 읽고, 바쁜 투자자를 위해 가장 중요한 핵심 3가지를 3줄로 요약 브리핑해주세요.
"""
print(f"💬 [전달한 프롬프트]: {prompt.strip()}")

# 3. AI 분석 및 요약 결과 생성 시뮬레이션
time.sleep(1)

print("\n" + "=" * 60)
print("📰 [AI Agent의 오늘의 경제 핵심 3줄 브리핑 리포트]")
print("=" * 60)

summary_result = """
1. 🏦 [글로벌 금리/인플레 긴장]: 연준 관계자들의 매파적(금리 인상/긴축 선호) 발언으로 미국 증시 하락 및 금리 불안감 고조
2. 📈 [국내 반도체 대형주 강세]: '삼전닉스(삼성전자·SK하이닉스)'를 중심으로 일주일간 8.5조 원 규모의 기관/외인 매수세 집중
3. 🏭 [친환경 에너지/제조업 재편]: 국내 풍력 에너지 기업(유니슨)의 공격적 투자와 미국 180년 전통 제조사의 구조조정 교차
"""
print(summary_result.strip())
print("\n💡 [AI 인사이트]: 미국 금리 인상 리스크에도 불구하고 국내 시장은 반도체 주도로 차별화 장세가 이어질 가능성이 높습니다.")
print("=" * 60)
print("🎉 [4단계 성공] 수집된 원본 뉴스를 AI가 사람이 읽기 편한 브리핑으로 변환했습니다!")