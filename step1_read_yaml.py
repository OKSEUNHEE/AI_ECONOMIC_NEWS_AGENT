import yaml

# 1. YAML 지시서 파일 열기
with open("configs/sources.yml", "r", encoding="utf-8") as f:
    # 2. YAML 글자를 파이썬 데이터(딕셔너리/리스트)로 변환
    data = yaml.safe_load(f)

# 3. 화면에 출력해보기
print("=" * 45)
print("🎉 [1단계 성공] YAML 파일 읽기 완료!")
print("=" * 45)
print(f"📌 총 등록된 뉴스 소스 개수: {len(data['sources'])}개\n")

for idx, src in enumerate(data['sources'], 1):
    print(f"[{idx}] {src['id']}")
    print(f"    - 국가: {src['country']}")
    print(f"    - 수집 방식: {src['type']}")
    if src['type'] == 'api':
        print(f"    - 엔드포인트: {src['endpoint']}")
    else:
        print(f"    - 타겟 사이트: {src['target_url']}")
    print()