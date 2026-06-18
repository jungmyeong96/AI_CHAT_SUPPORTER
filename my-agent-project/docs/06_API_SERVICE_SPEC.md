# BACKEND API SERVICE SPECIFICATION (FASTAPI)

## 1. 아키텍처 가이드 및 공통 서비스 레이어 (Architectural Standards)
> ⚠️ **AGENT 필수 준수 사항 (지속 개정 지원 프로토콜):**
> - 본 프로젝트는 Python 3.10+ 및 FastAPI 아키텍처 기반으로 구축됩니다. 향후 기능이 추가/수정될 경우, Agent는 본 문서의 엔드포인트 명세, DB 트랜잭션, 비즈니스 로직 제약 조건을 수시로 업데이트해야 합니다.
> - **의존성 주입 (Dependency Injection):** 데이터베이스 세션(`get_db`, `get_qdrant`)은 FastAPI `Depends` 구조를 통해 관리하며, 모든 SQLite 세션은 종료 직후 자원이 즉시 반환되도록 컨텍스트 매니저를 준수하십시오.

### [공통 1.1] Security & Compliance Service (준법 감시 레이어)
- **메커니즘:** 모든 인바운드 텍스트 수신 시 정규식 패턴 매칭 알고리즘을 선제 실행합니다.
- **마스킹 규칙:** 대한민국 주민등록번호(RRN) 및 민감 금융 식별정보 감지 시, 실제 데이터를 유출하지 않고 `[RRN Omitted]` 또는 `[Masked Financial Info]` 형태로 치환하여 DB에 안전하게 보존합니다. 위반 감지 시 `COMPLIANCE_YN = 1`을 반환합니다.

### [공통 1.2] AI & Vector Integration Service (AI 외부 연동 레이어)
- **Local LLM Engine:** Ollama API (`POST http://ollama:11434/api/generate`) 단일 싱글 스레드 세션 바인딩.
- **Vector DB Client:** Qdrant 내부 도커 브릿지 전용 엔드포인트 (`http://qdrant:6333`) 연결 및 커넥션 풀 공유.

---

## 2. 모듈별 세부 기능 및 API 라우터 명세 (Endpoint Specifications)

### MODULE 1. 대화 관리 모듈 (Chat Management)

#### F1. 채팅 이력 조회 (Chat History Read)
* **엔드포인트 및 프로토콜:** `GET /api/v1/chat/rooms/{room_id}/history` (HTTP REST)
* **연동 스토리지 및 자원:**
    * **Read:** SQLite `CHAT_HISTORY` 테이블, `USER_DEPT` 테이블
* **비즈니스 로직 및 제약 조건:**
    1. 대화방 식별자(`room_id`)를 기준으로 데이터베이스를 탐색하되, 논리적 삭제 플래그인 `USED_YN = 1`인 유효 레코드만 필터링합니다.
    2. 시간 정렬 정합성을 위해 `CREATED_TM` 컬럼 기준 **오름차순(ASC)** 정렬을 보장하십시오.
    3. 프론트엔드(`main.html`) 화면단에서 컴플라이언스(보안 가드) 작동 표시가 활성화될 수 있도록 각 메시지별 `COMPLIANCE_YN` 상태값을 누락 없이 JSON 결과 배열에 매핑해야 합니다.

#### F2. 신규 채팅 메시지 송신 (Chat History Create)
* **엔드포인트 및 프로토콜:** `POST /api/v1/chat/message` (HTTP REST 및 내부 브로드캐스팅 연동)
* **연동 스토리지 및 자원:**
    * **Create:** SQLite `CHAT_HISTORY`
    * **Read:** SQLite `USER_DEPT`
* **비즈니스 로직 및 제약 조건:**
    1. **컴플라이언스 필터 가동:** 메시지 저장 전 [공통 1.1] 보안 레이어를 통과시켜 계좌번호 및 주민번호 패턴을 마스킹 처리한 뒤 `MESSAGE` 컬럼에 적재합니다. 필터 적발 시 `COMPLIANCE_YN = 1`, 미적발 시 `0`으로 세팅합니다.
    2. 데이터가 디스크에 커밋된 즉시 HTTP Response 또는 구현된 이벤트를 트리거하여 프론트엔드가 타임라인 UI 화면을 즉시 갱신할 수 있도록 최신 적재 객체를 스펙에 맞춰 즉시 반환하십시오.

---

### MODULE 2. AI 추천 답변 엔진 모듈 (AI Recommendation Engine)

#### F3. AI 추천 답변 생성을 위한 질문 맥락 정제 및 융합
* **엔드포인트 및 프로토콜:** `POST /api/v1/ai/recommend/prepare` (HTTP REST)
* **연동 스토리지 및 자원:**
    * **Read:** Qdrant Vector DB (`collection: adopted_knowledge`), SQLite `CHAT_HISTORY`
    * **External System:** Ollama LLM 서버
* **비즈니스 로직 및 제약 조건:**
    1. **F3-1 (Query Reformulation):** 사용자가 선택한 원천 `CHAT_ID`와 직전 대화 맥락을 기반으로 Ollama를 1차 가동하여 RAG 성능 극대화를 위한 핵심 검색 키워드를 추출 및 정제(Query Reformulation)합니다.
    2. **F3-2 (Pre-Filtering & Weight Score Fusion):** - 검색 효율화를 위해 요청 사원의 `DEPT_CD`를 Qdrant의 Payload 필터로 우선 적용(Pre-filtering)하여 연산 대상을 격리합니다.
        - 매칭된 결과 중 가중치 유형(`selected_type`)에 따라 **① 공식 준법 가이드 (1.50배)**, **② 우수 채택 이력 (1.30배)**, **③ 일반 업무 이력 (1.00배)** 고유 가중치를 Cosine 유사도 점수에 결합 연산합니다.
    3. **최종 출력 바인딩:** 각 가중치 유형별 최상위 점수 데이터 1건씩 총 3건의 최종 추천 후보군을 조율된 프롬프트 프레임워크에 매핑하여 프론트엔드 모달(`modal.html`) 카드 레이아웃 규격에 맞게 JSON 스트림으로 전달하십시오.

---

### MODULE 3. 답변 채택 및 데이터 피드백 모듈 (Adoption & Feedback)

#### F4. AI 추천 답변 선택 및 채팅창 반영 (Adoption Trigger)
* **엔드포인트 및 프로토콜:** `POST /api/v1/ai/recommend/adopt` (HTTP REST)
* **연동 스토리지 및 자원:**
    * **Create/Upsert:** Qdrant Vector DB (`collection: adopted_knowledge`)
    * **Read:** SQLite `CHAT_HISTORY`
* **비즈니스 로직 및 제약 조건:**
    1. 사용자가 모달창에서 추천 카드를 선택하고 반영 버튼을 누르면 신규 UUID 기반 고유 식별자인 `ADOPT_ID`를 발급합니다.
    2. 선택된 지식 자산의 메타데이터 정보(`adopted_question`, `adopted_answer`, `selected_type`, `weight_score`)를 완벽히 구성하여 Qdrant 벡터 데이터베이스 스토리지에 실시간으로 `upsert`하여 지식 밀도를 즉시 동기화하십시오.

---

### MODULE 4. 백엔드 비동기 배치 워커 모듈 (Async Background Worker)

#### F5. [비동기-폴링] 주기적 대화쌍 종료 분석 및 벡터 적재 (cron / APScheduler)
* **구동 아키텍처:** FastAPI 백그라운드 단일 스레드 태스크 스케줄러 (1분 분할 주기 동작)
* **연동 스토리지 및 자원:**
    * **Read:** SQLite `CHAT_HISTORY`
    * **Create:** Qdrant Vector DB, SQLite 내 역추적 테이블
* **비즈니스 로직 및 제약 조건:**
    1. 아직 지식베이스화되지 않은 미정제 상태의 대화 로그를 `ROOM_ID` 단위 세션 뭉치로 주기적 스캔합니다.
    2. Ollama 추론 API를 호출하여 해당 대화가 타임아웃 규칙 혹은 맥락 분석에 의해 하나의 완결된 '업무 처리 세션'으로 완전히 종료되었는지 논리 판별합니다.
    3. 종결 판정 시 정제된 핵심 [질문-답변] 쌍을 자동으로 정제 가공하여 Qdrant 스토리지에 벡터 임베딩 및 메타 페이로드 형태로 배치 적재를 완수하십시오.

#### F6. [비동기-이벤트] 종결어구 감지 기반 실시간 대화쌍 정제 (Event Hook)
* **구동 아키텍처:** FastAPI 내부 라우터 가드 또는 미들웨어 인터셉트 훅(Hook)
* **연동 스토리지 및 자원:**
    * **Read:** SQLite `CHAT_HISTORY`
    * **Create:** Qdrant Vector DB
* **비즈니스 로직 및 제약 조건:**
    1. 사용자가 채팅 메시지에 "감사합니다", "수고하세요", "고맙습니다" 등의 대화 종결 프로세스 키워드를 전송하는 시점의 실시간 이벤트를 가로챕니다(Hook).
    2. 이벤트 감지 즉시 해당 대화방의 최근 타임라인 스트림을 즉각 역추적하여 Ollama LLM 서버에 컨텍스트 요약 지시를 전달합니다.
    3. 도출된 비정형 업무 지식의 핵심 구조를 추출 및 임베딩 처리하여 실시간 인덱싱 동기화를 완료하십시오.