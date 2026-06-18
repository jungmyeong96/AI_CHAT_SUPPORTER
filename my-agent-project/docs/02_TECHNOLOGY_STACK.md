# APPROVED TECHNOLOGY STACK & PACKAGE INTERCEPT RULES

## 1. 승인된 표준 기술 스택 (4-Core / 8GB RAM 최적화)
AI Agent는 코드를 생성, 수정하거나 패키지를 설치하는 모든 셸 명령을 수행할 때 반드시 지정된 기술 스택 영역 안에서만 움직여야 합니다. 

| 레이어 | 공인 기술 스택 (Tech Stack) | 개발 구현 조건 및 제약 |
| :--- | :--- | :--- |
| **Frontend** | React.js, TypeScript | TS Strict 모드 적용, 가벼운 렌더링 최적화, Tailwind CSS 사용 |
| **Backend** | Python, FastAPI | 비동기(`async/await`) 필수화 (싱글 스레드 효율 극대화용), `pydantic v2` |
| **Vector DB** | Qdrant | 메모리 및 CPU 소모를 줄이기 위해 On-disk 인덱싱 위주로 경량 설정 |
| **Local LLM** | Ollama (7B Parameter Under) | CPU 연산 속도 한계로 인해 무조건 **초경량 Q4_K_M 이하 양자화 모델**만 세팅 |
| **Async Batch** | 내장 cron / APScheduler | 추가 프로세스를 띄우지 않고 FastAPI 내부 이벤트 루프에 스케줄러 등록 |
| **SQL DB** | SQLite | 동시성 락(Lock)을 방지하기 위해 WAL(Write-Ahead Logging) 모드가 활성화된 내장 SQLite 사용 |
| **가상화** | Docker, Docker Compose | 멀티 컨테이너 자원 격리 배정 및 로컬 영속 볼륨 마운트 필수 유지 |
| **형상 관리** | Git | `.gitignore`에 `.db`, `node_modules`, `qdrant_storage` 필수 제외 |
| **API Docs** | Swagger UI | FastAPI 기본 라우터인 `/docs`를 통해 가볍게 작동 가능하도록 유지 |

## 2. 🚨 패키지 설치 무단 가동 차단 규칙 (CRITICAL INTERCEPT RULE)
> ⚠️ **AGENT 무조건 준수 사항:**
> 아래에 명시된 [사전 승인 라이브러리 목록] 외에 다른 파이썬 패키지나 npm 모듈이 필요하다고 판단되는 경우, **절대로 셸 명령어를 스스로 실행(`pip install`, `npm install`)하거나 `requirements.txt`/`package.json`에 임의로 추가하지 마십시오.**
> 반드시 셸 프롬프트나 대화창을 통해 **"사용자에게 해당 패키지가 필요한 이유와 명칭을 명확히 질문하고 허가가 떨어질 때까지 작업을 대기(Halt)"**해야 합니다.

### [사전 승인 라이브러리 목록]
- **Python:** `fastapi`, `uvicorn`, `pydantic`, `sqlite3`, `apscheduler`, `requests`, `httpx`
- **Node.js/TS:** `react`, `react-dom`, `typescript`, `axios`, `tailwindcss`

## 3. SQLite 튜닝 세팅 제약 (4-Core / WAL 모드)
FastAPI에서 SQLite 데이터베이스 커넥션을 맺을 때, 4코어 CPU 환경에서 읽기/쓰기 성능 저하 및 데이터베이스 락(Database Locked) 에러를 방지하기 위해 다음 프래그마(PRAGMA) 설정을 커넥션 직후 반드시 실행하도록 코드를 작성하십시오.
- 실행 구문 예시:
  conn.execute("PRAGMA journal_mode=WAL;")
  conn.execute("PRAGMA synchronous=NORMAL;")

## 4. Agent 태스크 자동 수행 규칙
1. **API 자동 등록 보장:** 백엔드 `main.py`에 새로운 엔드포인트를 추가할 때마다 Swagger UI 문서에 정상 노출되는지 스펙 구조를 수시로 교차 검증하십시오.
2. **도커 네트워크 정합성:** 프론트엔드가 백엔드(8000번 포트) 컨테이너와 안정적으로 인터페이스 통신을 주고받을 수 있도록 브릿지 네트워크 구성을 설계하십시오.