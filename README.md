# 🤖 AI Economic News Intelligence Agent
> **선언형(YAML) 수집 지시서 기반 다국적 경제 뉴스 자동 수집 및 AI 요약 에이전트**

[![Python 3.12](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-Automation-2EAD33?style=flat&logo=playwright&logoColor=white)](https://playwright.dev/)
[![YAML](https://img.shields.io/badge/Config-YAML-CB171E?style=flat&logo=yaml&logoColor=white)](https://yaml.org/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=flat&logo=github&logoColor=white)](https://github.com/OKSEUNHEE/AI_ECONOMIC_NEWS_AGENT)

---

## 📌 1. 프로젝트 개요 (Overview)

본 프로젝트는 사용자의 자연어 질문(예: *"미국 경제 뉴스 알려줘"*, *"오늘 한국 경제 뉴스 정리해줘"*)을 분석하여, **YAML 설정 지시서**를 바탕으로 최적의 수집 경로(**뉴스 API vs Playwright 웹 크롤러**)를 자율적으로 선택해 실시간 경제 뉴스를 수집하고 **AI 기반 핵심 브리핑 리포트**를 제공하는 **지능형 AI Agent 파이프라인**입니다.

---

## 🏗️ 2. 시스템 아키텍처 (Architecture)

```text
                  👤 사용자 (User)
                        │
                        │ "최근 미국 경제 뉴스 알려줘"
                        ▼
            🤖 AI Agent (Orchestrator)
            - 자연어 질문 의도 분석 (국가: US / 카테고리: 경제)
            - sources.yml 설정을 조회하여 수집 도구 자동 선택
                        │
          ┌─────────────┴─────────────┐
          ▼ (API 엔드포인트 지원 시)    ▼ (API 부재 / 동적 웹페이지 시)
    📡 News API Fetcher           🕷️ Playwright Web Crawler
    - Yahoo Finance API 호출         - CNBC / 네이버 경제 동적 렌더링
          │                           │
          ▼                           ▼
    [ Raw JSON Response ]       [ Parsed Web HTML ]
          └─────────────┬─────────────┘
                        ▼
            📦 Data Normalizer & Storage
            - 일관된 JSON 표준 스키마 변환 및 중복 기사 제거
                        │
                        ▼
            🧠 AI (LLM) Analyst Bridge
            - 기사 중요도 선별 및 카테고리 분류
            - 핵심 3줄 브리핑 & 투자자 인사이트 도출
                        │
                        ▼
                  👤 사용자에게 최종 브리핑 리포트 출력
```

---

## 🛠️ 3. 기술 스택 (Tech Stack)

| 구분 | 기술 / 라이브러리 | 역할 및 도입 이유 |
| :--- | :--- | :--- |
| **Language** | **Python 3.12+** | 비동기 지원 및 크롤링·데이터 처리·AI 파이프라인 통합 언어 |
| **Configuration** | **YAML (`PyYAML`)** | 코드 수정 없이 새로운 수집 사이트를 선언적으로 추가/관리하는 수집 지시서 |
| **Data Ingestion** | **`requests`, `json`** | 공개 뉴스 API 엔드포인트를 호출하여 초고속 정형 데이터 수집 |
| **Web Automation** | **`Microsoft Playwright`** | API가 없는 사이트(네이버, CNBC 등)를 Headless Chromium 브라우저로 렌더링 및 동적 크롤링 |
| **HTML Parsing** | **`BeautifulSoup4`, `lxml`** | 수집된 HTML DOM에서 CSS Selector 기반 뉴스 제목/링크 고속 파싱 |
| **AI & Agent** | **Agentic Tool-Calling** | 사용자 질문 의도 파악 ➔ 적정 도구(API vs Playwright) 자동 라우팅 ➔ 뉴스 요약 브리핑 생성 |
| **Dev Environment** | **WSL (Ubuntu), Git** | 리눅스 환경 개발, 가상환경(`venv`) 패키지 격리 및 GitHub 버전 관리 |

---

## 📂 4. 디렉터리 및 단계별 구현 구조

```text
AI_ECONOMIC_NEWS_AGENT/
│
├── configs/
│   └── sources.yml           # [Step 1] 국가별/주제별 수집 지시서 (API & Crawler 대상 정의)
│
├── step1_read_yaml.py        # [1단계] YAML 지시서 로더 및 검증 실습
├── step2_fetch_api.py        # [2단계] 뉴스 API (Yahoo Finance) 기반 초고속 JSON 수집 실습
├── step3_crawl_playwright.py # [3단계-A] 네이버 경제 뉴스 Playwright 크롤링 실습
├── step3_crawl_cnbc.py       # [3단계-B] 미국 CNBC 경제 뉴스 Playwright 크롤링 실습
├── step4_llm_summary.py      # [4단계] 수집 데이터 ➔ AI(LLM) 3줄 요약 브리핑 파이프라인 실습
├── step5_agent.py            # [5단계] 대화형 통합 AI Economic News Agent 실행기
│
├── requirements.txt          # 프로젝트 의존성 패키지 목록
└── README.md                 # 프로젝트 기술 문서
```

---

## 🚀 5. 실행 방법 (Quick Start)

### 1) 가상환경 활성화 및 패키지 설치
```bash
cd ~/AI_ECONOMIC_NEWS_AGENT
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### 2) 대화형 AI Agent 실행
```bash
python3 step5_agent.py
```

### 3) 질문 예시
```text
👤 나: 최근 미국 경제 뉴스 알려줘
👤 나: 오늘 한국 경제 뉴스 정리해줘
👤 나: q (종료)
```