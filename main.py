import sys
from core.agent import EconomicNewsAgent

def main():
    print("=" * 65)
    print("🤖 [AI Economic News Agent] 경제 뉴스 인텔리전스 에이전트 시작")
    print("=" * 65)
    print("💡 사용 예시:")
    print("   - '최근 미국 경제 뉴스 알려줘'")
    print("   - '오늘 한국 경제 뉴스 브리핑해줘'")
    print("   - '종합 글로벌 경제 뉴스 정리해줘'")
    print("   - 'exit' 또는 'q' 입력 시 종료")
    print("=" * 65)

    agent = EconomicNewsAgent("configs/sources.yml")

    while True:
        try:
            user_input = input("\n👤 나: ").strip()
            if not user_input:
                continue

            if user_input.lower() in ["q", "exit", "quit", "종료"]:
                print("\n👋 에이전트를 종료합니다. 좋은 하루 되세요!")
                break

            result = agent.process_query(user_input)

            if "error" in result:
                print(f"\n❌ [오류] {result['error']}")
                continue

            print("\n" + "=" * 65)
            print(result["briefing"])
            print("=" * 65)
            print(f"📁 상세 수집 데이터 파일: {result['saved_file']}\n")

        except KeyboardInterrupt:
            print("\n\n👋 프로그램을 종료합니다.")
            break
        except Exception as e:
            print(f"\n❌ 처리 중 오류 발생: {e}")

if __name__ == "__main__":
    main()