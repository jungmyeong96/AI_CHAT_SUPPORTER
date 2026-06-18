# SYSTEM ARCHITECTURE DESIGN & DOCKER ORCHESTRATION GUIDE

## 1. 아키텍처 개요 및 구성 요소 (Component Specifications)
> ⚠️ **AGENT 필수 지시사항 (4-Core / 8GB RAM 최적화):**
> 에이전트는 아래 정의된 구성 요소를 가상화(Docker) 인프라로 묶을 때, 하드웨어 자원 병목을 최소화하기 위해 RDB는 FastAPI 프로세스 내 임베디드 SQLite로 결합하고, 배치는 중량 프레임워크(Celery/Redis) 대신 FastAPI 내부 스케줄러(APScheduler/cron)로 경량화하여 구현해야 합니다.

### [1] 프론트엔드 (Web REACT)
* **기술 스택:** HTML5 / TypeScript (React.js)
* **UI 및 상태 관리:**
    * **발화 주체 토글:** "나(SM 개발자)" 혹은 "상대방" 스위치 토글 상태값에 따라 페이로드의 발화자 정보 바인딩.
    * **채팅 인터페이스:** 메시지 입력 시 백엔드 API (`POST /api/v1/chat/message`) 요청 전송 및 타임라인 갱신.
    * **지능형 추천 모달:** 추천 버튼 클릭 시 `/api/v1/ai/recommend/prepare` 호출 결과를 `modal.html` 규격에 맞춰 카드 뷰로 렌더링.
* **통신 프로토콜:** HTTP (REST) 통신 기반 데이터 교환.

### [2] 채팅-API 서버 (FastAPI)
* **기술 스택:** Python, FastAPI, Pydantic v2
* **엔드포인트 라우터 경로:** * `GET /api/v1/chat/rooms/{room_id}/history` (대화 이력 조회)
    * `POST /api/v1/chat/message` (채팅 메시지 적재 및 보안 필터링)
    * `POST /api/v1/ai/recommend/prepare` (가중치 기반 RAG 가동 및 Mock/실제 답변 생성)
* **핵심 비즈니스 로직 파이프라인:**
    1. 사용자 질문 수신 즉시 컴플라이언스(개인정보 마스킹) 가드 인터셉터 실행.
    2. 질문의 키워드 및 임베딩을 기반으로 Qdrant(벡터 DB) 검색 질의 요청.
    3. 준법(1.5), 우수(1.3), 일반(1.0) 가중치를 적용한 컨텍스트 프롬프트 융합(Fusion).
    4. Ollama(LLM)에 정제된 프롬프트를 전송하여 최종 가이드라인 답변 획득.
    5. 대화 및 최종 추천 데이터를 임베디드 SQLite DB에 즉시 영속화.

### [3] Qdrant (벡터 DB)
* **컨테이너 구성:** `collection: chat_knowledge`
* **데이터 세그먼트 구조:** `vector (임베딩 데이터) + payload (keyword, dept_cd, speaker, used_yn 등)`
* **에이전트 구현 규칙:** 4코어 환경에서의 CPU 오버헤드를 막기 위해 페이로드 필터링(Payload Filtering) 기능을 적극 활용하여 검색 범위를 사전 압축하도록 쿼리를 설계할 것.

### [4] LLM 서버 (Ollama)
* **엔진 및 모델:** Ollama (로컬 독립 컨테이너 운영, `Llama-3-8B-Instruct-Q4` 등 7B 이하 4-bit 양자화 모델 고정)
* **통신 프로토콜:** REST API (포트 11434) 기반 백엔드 연동.
* **추론 제약:** CPU 코어 스로틀링 방지를 위해 동시 추론 요청을 단일 세션으로 제어할 것.

### [5] 배치 워커 (Native cron / APScheduler)
* **역할 및 제약:** RAM 메모리 절약을 위해 **Celery 및 Redis의 추가 도입을 엄격히 금지**함. FastAPI 서버 내부에 임베디드된 가벼운 `cron (APScheduler)`을 단일 스레드로 구동할 것.
* **주요 메커니즘:** 주기적으로 SQLite의 `CHAT_HISTORY` 테이블을 스캔하여 완료된 대화 세션 분리 및 요약 처리를 비동기로 수행한 뒤, 최종 정제 데이터만 Qdrant 벡터DB에 증분 적재.

### [6] 관계형 DB (SQLite - Embedded)
* **물리 데이터베이스 파일:** `backend/backend_data/ai_assistant.db`
* **핵심 테이블 엔티티:**
    * `CHAT_ROOM`: 대화방 관리 정보 (ROOM_ID, ROOM_NAME, ROOM_TYPE)
    * `CHAT_HISTORY`: 원천 채팅 로그 및 보안 플래그 (CHAT_ID, ROOM_ID, EMP_ID, MESSAGE, COMPLIANCE_YN, USED_YN)
    * `ADOPTED_HISTORY`: 최종 채택 및 요약된 고가치 지식 자산쌍 (ADOPT_ID, CHAT_ID, EMP_ID, DEPT_CD, ADOPTED_QUESTION, ADOPTED_ANSWER, SELECTED_TYPE, WEIGHT_SCORE)
* **아키텍처 적용 규칙:** 별도의 외부 인스턴스를 띄우지 않고, FastAPI 서비스와 물리 볼륨 공유 및 커넥션 풀을 ContextManager로 제어하여 단일 컨테이너 안에서 경량 처리함.

---

## 2. 도커 컴포즈 인프라 명세 (Docker Compose Blueprint)

에이전트가 `docker-compose.yml` 및 하위 도커 파일을 작성할 때 무조건 적용해야 하는 격리 표준 사양입니다.

### [규칙 2.1] 4-Core / 8GB RAM 리소스 할당 가이드
호스트 OS의 다운 방지를 위해 도커 컴포즈 선언 시 아래 리소스 제약 조건을 하드코딩 형태로 반드시 삽입하십시오.

```yaml
version: '3.8'

networks:
  sm-agent-network:
    driver: bridge

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    networks:
      - sm-agent-network
    cpus: '0.5'
    mem_limit: 1024m

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/backend_data:/app/backend_data
    environment:
      - DATABASE_URL=sqlite:////app/backend_data/ai_assistant.db
    networks:
      - sm-agent-network
    cpus: '1.0'
    mem_limit: 1536m
    restart: always

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - ./qdrant_storage:/qdrant/storage
    networks:
      - sm-agent-network
    cpus: '0.5'
    mem_limit: 1024m

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ./ollama_storage:/root/.ollama
    networks:
      - sm-agent-network
    cpus: '2.0'
    mem_limit: 4096m