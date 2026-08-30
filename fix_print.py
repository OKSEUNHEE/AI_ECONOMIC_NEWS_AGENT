from tools.company_resolver import CompanyResolver

# step5_agent.py의 출력 중복 수정
with open("step5_agent.py", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("💰 실시간 현재 주가: {res['price']} {res['currency']}", "💰 실시간 현재 가격: {res['price']}")

with open("step5_agent.py", "w", encoding="utf-8") as f:
    f.write(code)